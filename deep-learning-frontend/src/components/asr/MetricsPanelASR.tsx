'use client'

import type { ASRResponse } from '@/types/asr'

interface MetricsPanelASRProps {
  data: ASRResponse
}

function MetricCard({ label, value, sub, accent = false }: { label: string; value: string; sub: string; accent?: boolean }) {
  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-600 dark:bg-slate-700/50">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">{label}</p>
      <p className={`mt-1.5 text-xl font-bold leading-none ${accent ? 'text-[#1E3A5F] dark:text-blue-400' : 'text-slate-800 dark:text-slate-200'}`}>
        {value}
      </p>
      <p className="mt-1.5 text-[11px] text-slate-400 dark:text-slate-500">{sub}</p>
    </div>
  )
}

export default function MetricsPanelASR({ data }: MetricsPanelASRProps) {
  return (
    <div className="space-y-4">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">Metricas</p>
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Confianza" value={`${(data.confidence * 100).toFixed(1)}%`} sub="score del modelo CTC" accent />
        <MetricCard label="Duracion" value={`${data.duration_s.toFixed(1)} s`} sub="audio recibido" accent />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Latencia" value={`${data.latency_ms.toFixed(0)} ms`} sub={data.model} />
        <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-600 dark:bg-slate-700/50">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">Transcripcion normalizada</p>
          <p className="mt-1.5 text-xs font-medium text-slate-700 leading-relaxed line-clamp-3 dark:text-slate-300">
            {data.normalized_transcription || '—'}
          </p>
        </div>
      </div>
    </div>
  )
}
