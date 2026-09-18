#!/bin/bash
# Setup script for cloud deployment
# This script generates secrets and prepares your project for deployment

set -e

echo "🚀 AI Power Coding Tutor - Cloud Deployment Setup"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi
echo "✓ Python 3 found"

if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed"
    exit 1
fi
echo "✓ Git found"

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not a Git repository"
    exit 1
fi
echo "✓ Git repository found"

echo ""
echo "${BLUE}Checking if working directory is clean...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: There are uncommitted changes"
    echo "   Please commit or stash changes before deploying"
    git status
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo "✓ Working directory clean"

echo ""
echo "${BLUE}Generating secure secrets...${NC}"

# Generate JWT Secret
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "✓ JWT Secret generated"

# Generate Database password
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
echo "✓ Database password generated"

echo ""
echo "${YELLOW}Generated Secrets:${NC}"
echo "==================="
echo "${GREEN}JWT_SECRET:${NC}"
echo "$JWT_SECRET"
echo ""
echo "${GREEN}DATABASE PASSWORD:${NC}"
echo "$DB_PASSWORD"
echo ""

echo "${YELLOW}Next Steps:${NC}"
echo "==========="
echo ""
echo "1. Create accounts (if not already done):"
echo "   - Vercel: https://vercel.com/signup"
echo "   - Render: https://render.com/signup"
echo "   - Google Gemini: https://ai.google.dev"
echo ""

echo "2. Deploy PostgreSQL on Render:"
echo "   - Go to https://render.com/dashboard"
echo "   - Create new PostgreSQL database"
echo "   - Database: ai_coding_tutor"
echo "   - User: tutor"
echo "   - Password: ${DB_PASSWORD}"
echo "   - Copy the connection string"
echo ""

echo "3. Deploy Backend on Render:"
echo "   - Create new Web Service from GitHub"
echo "   - Root directory: backend"
echo "   - Set environment variables:"
echo "     - DATABASE_URL: (from step 2)"
echo "     - JWT_SECRET: ${JWT_SECRET}"
echo "     - AI_PROVIDER: gemini"
echo "     - GEMINI_API_KEY: (from Google Gemini)"
echo "     - CORS_ORIGINS: (will update after frontend deploy)"
echo ""

echo "4. Deploy Frontend on Vercel:"
echo "   - Import GitHub repository"
echo "   - Root directory: frontend"
echo "   - Set environment variables:"
echo "     - VITE_API_URL: (from Render backend service)"
echo ""

echo "5. Update CORS on Render:"
echo "   - Update CORS_ORIGINS with Vercel frontend URL"
echo ""

echo "6. Configure GitHub Actions (optional but recommended):"
echo "   - Add GitHub secrets:"
echo "     - RENDER_DEPLOY_HOOK"
echo "     - VERCEL_TOKEN"
echo "     - VERCEL_ORG_ID"
echo "     - VERCEL_PROJECT_ID"
echo ""

echo "${GREEN}✓ Setup script complete!${NC}"
echo ""
echo "For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo "For deployment checklist, see: DEPLOYMENT_CHECKLIST.md"
echo ""

# Save secrets to a temporary file (user should save this securely)
SECRETS_FILE="deployment-secrets-$(date +%s).txt"
cat > "$SECRETS_FILE" << EOF
🔒 DEPLOYMENT SECRETS - KEEP THIS SAFE 🔒
Generated: $(date)

JWT_SECRET=$JWT_SECRET

DATABASE PASSWORD=$DB_PASSWORD

AI API KEYS:
- Google Gemini: (get from https://ai.google.dev)
- OpenAI: (get from https://platform.openai.com, optional)

IMPORTANT:
1. Save this file in a password manager (LastPass, 1Password, etc.)
2. Do NOT commit this file to Git
3. Do NOT share this file
4. Delete this file after saving the secrets safely
EOF

echo "📝 Secrets saved to: $SECRETS_FILE"
echo "   Please save these secrets in a password manager and delete the file"
echo ""

# Add secrets file to gitignore
if ! grep -q "deployment-secrets-" .gitignore 2>/dev/null; then
    echo "deployment-secrets-*.txt" >> .gitignore
    echo "✓ Added secrets file pattern to .gitignore"
fi

echo ""
echo "🎉 Ready to deploy!"
