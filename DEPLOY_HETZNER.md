# Deploying to Hetzner Cloud

Everything runs on one VM with Docker:

```
Internet ──443──▶ web (Caddy: HTTPS + React static files)
                    └── /api/* ──▶ backend (FastAPI) ──▶ db (Postgres 16)
                                     └── Docker socket ──▶ ai-tutor-runner-{python,java,ruby}
                                                           (one throwaway container per submission)
```

Only ports 22, 80 and 443 are reachable from outside. Postgres and the API are internal.

## 1. Create the server (~€4–8/month)

1. Sign up at <https://console.hetzner.cloud> and create a project.
2. **Add Server**:
   - Location: closest to your users (e.g. Helsinki/Falkenstein for EU, Ashburn for US, Singapore for Asia)
   - Image: **Ubuntu 24.04**
   - Type: **CX22** (2 vCPU, 4 GB): enough for a class-sized load. Pick CX32 (8 GB) if many students will run Java at once.
   - SSH key: add your public key (`cat ~/.ssh/id_ed25519.pub`). Don't use password login.
3. Note the server's public IPv4.

## 2. Point a domain at it

At your DNS provider, create an **A record**, e.g. `tutor.yourdomain.com → <server IP>`.
Caddy needs this record to resolve before it can issue the HTTPS certificate.

## 3. Provision the server (once)

```bash
ssh root@<server-ip>
curl -fsSL https://raw.githubusercontent.com/Karthiga08/ai-power-coding-tutor/main/deploy/server-setup.sh | bash
```

This installs Docker, enables the firewall, adds 2 GB swap, creates a `deploy`
user (with your SSH key), and clones the repo to `/opt/ai-tutor`.

## 4. Configure secrets

```bash
su - deploy
cd /opt/ai-tutor
cp .env.hetzner.example .env
nano .env
```

Fill in `DOMAIN`, `ACME_EMAIL`, `POSTGRES_PASSWORD`, `JWT_SECRET` and your
`GEMINI_API_KEY` (or `OPENAI_API_KEY` with `AI_PROVIDER=openai`). Generate secrets with:

```bash
openssl rand -hex 32
```

## 5. Deploy

```bash
./deploy/deploy.sh
```

The first run takes a few minutes (it builds the runner images, backend and frontend).
When it prints `Up: https://<your domain>`, open that URL.

## 6. Seed course content (once)

```bash
c="docker compose -f docker-compose.prod.yml exec backend"
$c python seed.py
$c python seed_more_courses.py
$c python seed_java_ruby_problems.py
$c python seed_extra_lessons.py
$c python seed_python_oop_errors.py
$c python seed_more_quiz_questions.py
$c python seed_prompt_engineering.py
$c python seed_quicksort_mergesort.py
$c python seed_remaining_problems.py
$c python seed_trees_graphs_impl.py
```

Change the seeded admin password right after logging in.

## 7. Backups

```bash
crontab -e
# add:
15 3 * * * /opt/ai-tutor/deploy/backup-db.sh >> /opt/ai-tutor/backups/backup.log 2>&1
```

Also enable **Backups** on the server in the Hetzner console (+20% of server price)
for full-disk snapshots. Restore a dump with:

```bash
gunzip -c backups/db-XXXX.sql.gz | docker compose -f docker-compose.prod.yml exec -T db psql -U tutor ai_coding_tutor
```

## 8. Auto-deploy on push (optional)

`.github/workflows/deploy.yml` builds the frontend, then SSHes in and runs `deploy/deploy.sh`.

1. On your laptop: `ssh-keygen -t ed25519 -f gh_deploy -N ""`
2. On the server as `deploy`: append `gh_deploy.pub` to `~/.ssh/authorized_keys`
3. In GitHub → Settings → Secrets and variables → Actions, add:
   - `HETZNER_HOST`: the server IP
   - `HETZNER_SSH_KEY`: contents of `gh_deploy` (the private key)

## Day-to-day

| Task | Command (in `/opt/ai-tutor`) |
|---|---|
| Update to latest `main` | `./deploy/deploy.sh` |
| Logs | `docker compose -f docker-compose.prod.yml logs -f backend` |
| Status | `docker compose -f docker-compose.prod.yml ps` |
| Restart | `docker compose -f docker-compose.prod.yml restart backend` |
| DB shell | `docker compose -f docker-compose.prod.yml exec db psql -U tutor ai_coding_tutor` |

## Security notes

- **Docker socket.** The backend mounts `/var/run/docker.sock` so `code_runner.py`
  can start sandbox containers. Anyone who gets code execution *inside the backend
  container* effectively has root on the VM. Student code itself runs in the
  separate runner containers (no network, capped CPU/memory/PIDs, non-root user,
  10 s timeout), not in the backend. Keep this VM dedicated to this app, and don't
  store anything else on it.
- **Stronger isolation (later).** Install [gVisor](https://gvisor.dev) and pass
  `runtime="runsc"` in `client.containers.create(...)` so student code runs under a
  user-space kernel. Or move code execution to a separate small VM.
- **AI cost.** `/api/ai` calls a paid LLM API on every request. Keep registration
  limited or add rate limiting before sharing the URL widely.
