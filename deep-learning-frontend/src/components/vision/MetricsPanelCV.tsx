'use client'

import type { VisionResponse } from '@/types/vision'

interface MetricsPanelCVProps {
  data: VisionResponse
}

function MetricCard({
  label, value, sub, accent = false, highlight,
}: {
  label: string; value: string; sub: string; accent?: boolean; highlight?: 'positive' | 'negative'
}) {
  const valueColor =
    highlight === 'positive' ? 'text-emerald-700 dark:text-emerald-400' :
    highlight === 'negative' ? 'text-red-600 dark:text-red-400'         :
    accent                   ? 'text-[#1E3A5F] dark:text-blue-400'      :
                               'text-slate-800 dark:text-slate-200'

  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-600 dark:bg-slate-700/50">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">{label}</p>
      <p className={`mt-1.5 text-xl font-bold leading-none ${valueColor}`}>{value}</p>
      <p className="mt-1.5 text-[11px] text-slate-400 dark:text-slate-500">{sub}</p>
    </div>
  )
}

export default function MetricsPanelCV({ data }: MetricsPanelCVProps) {
  return (
    <div className="space-y-4">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">Metricas</p>
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Resultado" value={data.has_tumor ? 'Tumor detectado' : 'Sin tumor'} sub="clasificacion binaria" highlight={data.has_tumor ? 'negative' : 'positive'} />
        <MetricCard label="Probabilidad media" value={`${(data.average_tumor_probability * 100).toFixed(1)}%`} sub="promedio en region tumoral" accent />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Area tumoral" value={`${data.tumor_area_percentage.toFixed(2)}%`} sub="del total de la imagen" accent />
        <MetricCard label="Latencia" value={`${data.latency_ms.toFixed(0)} ms`} sub={data.model} />
      </div>
    </div>
  )
}
