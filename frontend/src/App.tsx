export default function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center px-6 py-12">
        <section className="w-full rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-cyan-950/30 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.35em] text-cyan-300">CartoonVerse</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-6xl">
            Classical cartoonization for images and video.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            This scaffold is ready for the FastAPI backend, the React upload UI, and the worker pipeline.
          </p>
          <div className="mt-8 flex flex-wrap gap-3 text-sm text-slate-200">
            <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2">FastAPI</span>
            <span className="rounded-full border border-fuchsia-400/30 bg-fuchsia-400/10 px-4 py-2">Vite React</span>
            <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-4 py-2">Celery + Redis</span>
          </div>
        </section>
      </div>
    </main>
  );
}
