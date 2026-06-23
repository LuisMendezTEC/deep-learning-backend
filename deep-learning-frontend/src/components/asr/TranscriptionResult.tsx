'use client'

import type { ASRResponse } from '@/types/asr'

interface TranscriptionResultProps {
  result: ASRResponse
}

export default function TranscriptionResult({ result }: TranscriptionResultProps) {
  const pct = Math.round(result.confidence * 100)

  const barColor =
    result.confidence >= 0.85 ? 'bg-emerald-500' :
    result.confidence >= 0.6  ? 'bg-amber-400'   : 'bg-red-500'

  const labelColor =
    result.confidence >= 0.85 ? 'text-emerald-700 dark:text-emerald-400' :
    result.confidence >= 0.6  ? 'text-amber-600 dark:text-amber-400'     : 'text-red-600 dark:text-red-400'

  const confidenceLabel =
    result.confidence >= 0.85 ? 'Alta confianza' :
    result.confidence >= 0.6  ? 'Confianza moderada' : 'Baja confianza'

  const wordCount = result.transcription.trim()
    ? result.transcription.trim().split(/\s+/).length
    : 0

  return (
    <div className="space-y-4">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
        Transcripcion
      </p>

      <div className="rounded-xl border border-slate-100 bg-slate-50 p-5 dark:border-slate-600 dark:bg-slate-700/50">
        {result.transcription ? (
          <p className="text-base font-medium leading-relaxed text-slate-800 dark:text-slate-200">
            {result.transcription}
          </p>
        ) : (
          <p className="text-sm italic text-slate-400 dark:text-slate-500">Sin texto transcrito.</p>
        )}

        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-slate-400 dark:text-slate-500">{wordCount} palabras</span>
          <span className={`text-xs font-semibold ${labelColor}`}>
            {confidenceLabel} · {pct}%
          </span>
        </div>

        <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-600">
          <div className={`h-1 rounded-full transition-all duration-500 ${barColor}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  )
}
