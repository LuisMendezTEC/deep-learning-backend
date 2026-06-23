'use client'

import { useState, useRef, useCallback } from 'react'

interface ImageUploaderProps {
  onFileSelect: (file: File, preview: string) => void
  disabled?: boolean
}

const MAX_SIZE_MB = 10
const ACCEPTED_TYPES = new Set(['image/png', 'image/jpeg', 'image/tiff', 'image/tif'])
const ACCEPTED_EXTENSIONS = '.png,.jpg,.jpeg,.tiff,.tif'

export default function ImageUploader({ onFileSelect, disabled = false }: ImageUploaderProps) {
  const [preview, setPreview]       = useState<string | null>(null)
  const [fileName, setFileName]     = useState<string | null>(null)
  const [dragOver, setDragOver]     = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const processFile = useCallback(
    (file: File) => {
      setLocalError(null)
      if (!ACCEPTED_TYPES.has(file.type)) {
        setLocalError('Formato no soportado. Usa PNG, JPG o TIFF.')
        return
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setLocalError(`El archivo supera el limite de ${MAX_SIZE_MB} MB.`)
        return
      }
      const reader = new FileReader()
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string
        setPreview(dataUrl)
        setFileName(file.name)
        onFileSelect(file, dataUrl)
      }
      reader.readAsDataURL(file)
    },
    [onFileSelect],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) processFile(file)
    },
    [processFile],
  )

  return (
    <div className="space-y-3">
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !disabled && inputRef.current?.click()}
        className={[
          'relative flex min-h-[180px] flex-col items-center justify-center gap-3',
          'rounded-xl border-2 border-dashed p-6 cursor-pointer transition-colors duration-200',
          disabled ? 'opacity-50 cursor-not-allowed' : '',
          dragOver
            ? 'border-[#1E3A5F] bg-[#EFF6FF] dark:border-blue-500 dark:bg-blue-900/20'
            : 'border-slate-200 bg-slate-50 hover:border-[#1E3A5F]/40 hover:bg-blue-50/40 dark:border-slate-600 dark:bg-slate-700/50 dark:hover:border-blue-600/40 dark:hover:bg-blue-900/10',
        ].join(' ')}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
          disabled={disabled}
          className="hidden"
        />

        {preview ? (
          <div className="flex flex-col items-center gap-2 w-full">
            <img src={preview} alt="Vista previa" className="max-h-44 rounded-lg object-contain" />
            <p className="text-xs text-slate-400 dark:text-slate-500 truncate max-w-full px-2">{fileName}</p>
            <p className="text-xs text-[#1E3A5F]/70 dark:text-blue-400/70">Clic para cambiar imagen</p>
          </div>
        ) : (
          <>
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-600">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>
              </svg>
            </div>
            <div className="text-center space-y-1">
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Arrastra tu imagen MRI aqui</p>
              <p className="text-xs text-slate-400 dark:text-slate-500">o haz clic para seleccionar</p>
            </div>
            <p className="text-xs text-slate-300 dark:text-slate-600">PNG · JPG · TIFF · Max. 10 MB</p>
          </>
        )}
      </div>

      {localError && (
        <p className="text-xs text-red-500 dark:text-red-400 text-center">{localError}</p>
      )}
    </div>
  )
}
