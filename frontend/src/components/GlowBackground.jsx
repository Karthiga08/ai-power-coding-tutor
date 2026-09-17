export default function GlowBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute -top-40 -left-40 w-[30rem] h-[30rem] rounded-full bg-teal-500/20 blur-[100px]" />
      <div className="absolute top-1/3 -right-40 w-[26rem] h-[26rem] rounded-full bg-cyan-400/10 blur-[110px]" />
      <div className="absolute bottom-0 left-1/4 w-[24rem] h-[24rem] rounded-full bg-sky-600/15 blur-[100px]" />
    </div>
  );
}
