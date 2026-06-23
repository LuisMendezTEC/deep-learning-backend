'use client'

interface LoadingStateProps {
  message?: string
}

export default function LoadingState({ message = 'Procesando...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-14">
      <div className="h-8 w-8 rounded-full border-[3px] border-slate-200 border-t-[#1E3A5F] animate-spin dark:border-slate-700 dark:border-t-blue-500" />
      <p className="text-sm text-slate-500 dark:text-slate-400">{message}</p>
    </div>
  )
}
