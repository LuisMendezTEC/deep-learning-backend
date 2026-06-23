'use client'

import { useState } from 'react'
import AudioRecorder from '@/components/asr/AudioRecorder'
import TranscriptionResult from '@/components/asr/TranscriptionResult'
import MetricsPanelASR from '@/components/asr/MetricsPanelASR'
import LoadingState from '@/components/ui/LoadingState'
import ErrorBanner from '@/components/ui/ErrorBanner'
import { transcribeAudio } from '@/lib/api'
import type { ASRResponse } from '@/types/asr'

export default function ASRPage() {
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [reference, setReference] = useState('')
  const [result, setResult]       = useState<ASRResponse | null>(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<Error | null>(null)

  const handleAudioReady = (file: File) => {
    setAudioFile(file); setResult(null); setError(null)
  }

  const handleSubmit = async () => {
    if (!audioFile) return
    setLoading(true); setError(null); setResult(null)
    try {
      setResult(await transcribeAudio(audioFile, reference.trim() || undefined, 'es'))
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
        <p className="mb-1 text-xs font-medium uppercase tracking-widest text-slate-400 dark:text-slate-500">Modulo ASR</p>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">Reconocimiento de Voz</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Graba o sube un archivo de audio en español para transcribirlo automaticamente.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: inputs */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
            <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
              Audio
            </p>
            <AudioRecorder onAudioReady={handleAudioReady} disabled={loading} />
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
            <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500">
              Transcripcion de Referencia{' '}
              <span className="normal-case font-normal">(opcional)</span>
            </p>
            <p className="mb-3 text-xs text-slate-400 dark:text-slate-500">
              Proporciona el texto real para calcular WER y CER.
            </p>
            <textarea
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              placeholder="el nino corre por el parque..."
              disabled={loading}
              rows={3}
              className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[#1E3A5F] focus:outline-none focus:ring-1 focus:ring-[#1E3A5F]/20 disabled:opacity-50 transition-colors dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200 dark:placeholder:text-slate-600 dark:focus:border-blue-500 dark:focus:ring-blue-500/20"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!audioFile || loading}
            className="w-full rounded-xl bg-[#1E3A5F] py-3 text-sm font-semibold text-white transition-colors hover:bg-[#16304F] disabled:cursor-not-allowed disabled:opacity-40 dark:bg-blue-700 dark:hover:bg-blue-600"
          >
            {loading ? 'Transcribiendo...' : 'Transcribir audio'}
          </button>

          <ErrorBanner error={error} onDismiss={() => setError(null)} />
        </div>

        {/* Right: results */}
        <div className="space-y-4">
          {loading && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
              <LoadingState message="Transcribiendo audio..." />
            </div>
          )}

          {result && (
            <>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
                <TranscriptionResult result={result} />
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-700 dark:bg-slate-800">
                <MetricsPanelASR data={result} />
              </div>
            </>
          )}

          {!result && !loading && (
            <div className="flex h-full min-h-[240px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-16 text-center shadow-card dark:border-slate-700 dark:bg-slate-800">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>
                </svg>
              </div>
              <p className="text-sm text-slate-400 dark:text-slate-500">La transcripcion aparecera aqui</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
