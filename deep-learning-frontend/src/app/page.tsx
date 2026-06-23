import Link from 'next/link'

const VISION_TAGS = ['U-Net', 'ResNet-50', 'EfficientNet-B4', 'Segmentación semántica']
const ASR_TAGS   = ['CNN + BiLSTM', 'CTC Decoding', 'Mel Spectrogram', 'Mozilla Common Voice']

export default function Home() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-20">

      {/* Hero */}
      <div className="mb-16 space-y-5 text-center">
        <span className="inline-block rounded-full border border-slate-200 bg-white px-4 py-1 text-xs font-medium text-slate-500 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
          Proyecto Programado II · TEC · 2026
        </span>
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl dark:text-slate-50">
          Deep Learning Inference Platform
        </h1>
        <p className="mx-auto max-w-xl text-base leading-relaxed text-slate-500 dark:text-slate-400">
          Inferencia de modelos de deep learning para segmentación de tumores cerebrales en MRI
          y reconocimiento automático de voz en español.
        </p>
      </div>

      {/* Module cards */}
      <div className="grid gap-5 sm:grid-cols-2">
        <Link
          href="/vision"
          className="group rounded-2xl border border-slate-200 bg-white p-8 shadow-card transition-all duration-200 hover:shadow-card-hover hover:border-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-blue-800"
        >
          <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-xl bg-[#EFF6FF] text-[#1E3A5F] dark:bg-blue-900/40 dark:text-blue-300">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <h2 className="mb-2 text-lg font-semibold text-slate-900 transition-colors group-hover:text-[#1E3A5F] dark:text-slate-100 dark:group-hover:text-blue-400">
            Modulo de Vision
          </h2>
          <p className="mb-5 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
            Segmentación semantica de tumores cerebrales en imagenes MRI (LGG) mediante
            U-Net con backbones ResNet-50 y EfficientNet-B4.
          </p>
          <div className="mb-6 flex flex-wrap gap-2">
            {VISION_TAGS.map((tag) => (
              <span
                key={tag}
                className="rounded-md border border-blue-100 bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:border-blue-900 dark:bg-blue-900/30 dark:text-blue-300"
              >
                {tag}
              </span>
            ))}
          </div>
          <span className="inline-flex items-center gap-1 text-sm font-medium text-[#1E3A5F] transition-transform group-hover:translate-x-0.5 dark:text-blue-400">
            Ir al modulo
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </span>
        </Link>

        <Link
          href="/asr"
          className="group rounded-2xl border border-slate-200 bg-white p-8 shadow-card transition-all duration-200 hover:shadow-card-hover hover:border-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-blue-800"
        >
          <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-xl bg-[#EFF6FF] text-[#1E3A5F] dark:bg-blue-900/40 dark:text-blue-300">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>
            </svg>
          </div>
          <h2 className="mb-2 text-lg font-semibold text-slate-900 transition-colors group-hover:text-[#1E3A5F] dark:text-slate-100 dark:group-hover:text-blue-400">
            Modulo ASR
          </h2>
          <p className="mb-5 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
            Reconocimiento automatico de voz en español mediante CNN + BiLSTM con
            decodificación CTC, entrenado sobre Mozilla Common Voice.
          </p>
          <div className="mb-6 flex flex-wrap gap-2">
            {ASR_TAGS.map((tag) => (
              <span
                key={tag}
                className="rounded-md border border-blue-100 bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:border-blue-900 dark:bg-blue-900/30 dark:text-blue-300"
              >
                {tag}
              </span>
            ))}
          </div>
          <span className="inline-flex items-center gap-1 text-sm font-medium text-[#1E3A5F] transition-transform group-hover:translate-x-0.5 dark:text-blue-400">
            Ir al modulo
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </span>
        </Link>
      </div>

      {/* Architecture */}
      <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-8 shadow-card dark:border-slate-700 dark:bg-slate-800">
        <h3 className="mb-6 text-sm font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
          Arquitectura del Sistema
        </h3>
        <div className="flex items-center gap-4">
          <div className="flex-1 rounded-xl border border-slate-100 bg-slate-50 p-5 text-center dark:border-slate-700 dark:bg-slate-700/50">
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Frontend</p>
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Next.js · TypeScript · Tailwind CSS</p>
          </div>
          <div className="shrink-0 text-slate-300 dark:text-slate-600">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div className="flex-1 rounded-xl border border-slate-100 bg-slate-50 p-5 text-center dark:border-slate-700 dark:bg-slate-700/50">
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Backend API</p>
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">FastAPI · PyTorch · Python 3.11</p>
          </div>
        </div>
      </div>

    </div>
  )
}
