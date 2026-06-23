'use client'

import type { VisionResponse } from '@/types/vision'

interface SegmentationResultProps {
  result: VisionResponse
  originalPreview: string
}

function ImageCard({ src, label }: { src: string; label: string }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="text-center text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
        {label}
      </p>
      <div className="overflow-hidden rounded-xl border border-slate-100 bg-slate-900 dark:border-slate-700">
        <img src={src} alt={label} className="w-full object-contain" />
      </div>
    </div>
  )
}

export default function SegmentationResult({ result, originalPreview }: SegmentationResultProps) {
  return (
    <div className="space-y-4">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
        Resultado de segmentacion
      </p>
      <div className="grid grid-cols-3 gap-3">
        <ImageCard src={originalPreview}                                   label="Original" />
        <ImageCard src={`data:image/png;base64,${result.mask}`}            label="Mascara"  />
        <ImageCard src={`data:image/png;base64,${result.segmented_image}`} label="Overlay"  />
      </div>
    </div>
  )
}
