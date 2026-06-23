'use client'

import { useState, useCallback } from 'react'
import ImageUploader from '@/components/vision/ImageUploader'
import SegmentationResult from '@/components/vision/SegmentationResult'
import MetricsPanelCV from '@/components/vision/MetricsPanelCV'
import LoadingState from '@/components/ui/LoadingState'
import ErrorBanner from '@/components/ui/ErrorBanner'
import { segmentImage } from '@/lib/api'
import type { VisionResponse, BackboneType } from '@/types/vision'

const BACKBONES: { value: BackboneType; label: string; desc: string }[] = [
  { value: 'resnet50',        label: 'ResNet-50',       desc: 'Rapido y robusto' },
  { value: 'efficientnet-b4', label: 'EfficientNet-B4', desc: 'Mayor precision' },
]

export default function VisionPage() {
  const [file, setFile]         = useState<File | null>(null)
  const [preview, setPreview]   = useState<string | null>(null)
  const [backbone, setBackbone] = useState<BackboneType>('resnet50')
  const [result, setResult]     = useState<VisionResponse | null>(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<Error | null>(null)

  const handleFileSelect = useCallback((f: File, dataUrl: string) => {
    setFile(f); setPreview(dataUrl); setResult(null); setError(null)
  }, [])

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true); setError(null); setResult(null)
    try {
      setResult(await segmentImage(file, backbone, true))
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Error desconocido'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      {/* Page header */}
      <div className="mb-8 border-b border-slate-200 pb-6 dark:border-slate-800">
        <p className="mb-1 text-xs font-medium uppercase tracking-widest text-slate-400 dark:text-slate-500">Modulo de Vision</p>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">Segmentacion de MRI</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Sube una imagen de resonancia magnetica cerebral para detectar y segmentar el tumor.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: inputs */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
            <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
              Imagen MRI
            </p>
            <ImageUploader onFileSelect={handleFileSelect} disabled={loading} />
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
            <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
              Backbone del Modelo
            </p>
            <div className="grid grid-cols-2 gap-3">
              {BACKBONES.map((b) => (
                <button
                  key={b.value}
                  onClick={() => { setBackbone(b.value); setResult(null) }}
                  disabled={loading}
                  className={[
                    'rounded-xl border p-4 text-left transition-all disabled:cursor-not-allowed disabled:opacity-50',
                    backbone === b.value
                      ? 'border-[#1E3A5F] bg-[#EFF6FF] text-[#1E3A5F] dark:border-blue-500 dark:bg-blue-900/30 dark:text-blue-300'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300 hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-700/50 dark:text-slate-400 dark:hover:border-slate-500 dark:hover:bg-slate-700',
                  ].join(' ')}
                >
                  <p className="text-sm font-semibold">{b.label}</p>
                  <p className="mt-0.5 text-xs opacity-60">{b.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="w-full rounded-xl bg-[#1E3A5F] py-3 text-sm font-semibold text-white transition-colors hover:bg-[#16304F] disabled:cursor-not-allowed disabled:opacity-40 dark:bg-blue-700 dark:hover:bg-blue-600"
          >
            {loading ? 'Procesando...' : 'Segmentar imagen'}
          </button>

          <ErrorBanner error={error} onDismiss={() => setError(null)} />
        </div>

        {/* Right: results */}
        <div className="space-y-4">
          {loading && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
              <LoadingState message="Ejecutando inferencia..." />
            </div>
          )}

          {result && preview && (
            <>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
                <SegmentationResult result={result} originalPreview={preview} />
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
                <MetricsPanelCV data={result} />
              </div>
            </>
          )}

          {!result && !loading && (
            <div className="flex h-full min-h-[240px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-16 text-center shadow-card dark:border-slate-700 dark:bg-slate-800">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                </svg>
              </div>
              <p className="text-sm text-slate-400 dark:text-slate-500">El resultado aparecera aqui</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
