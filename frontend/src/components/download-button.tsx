"use client"

import { Download, CheckCircle, Clock } from "lucide-react"

interface DownloadButtonProps {
  isEnabled: boolean
  pendingCount: number
  onDownload: () => void
}

export default function DownloadButton({ isEnabled, pendingCount, onDownload }: DownloadButtonProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={onDownload}
        disabled={!isEnabled}
        className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
          isEnabled
            ? "bg-green-600 text-white hover:bg-green-700 hover:shadow-lg transform hover:scale-105"
            : "bg-gray-300 text-gray-500 cursor-not-allowed"
        }`}
      >
        <Download className="w-4 h-4" />
        Download Enriched JSON
      </button>

      {/* Status indicator */}
      <div className="flex items-center gap-2 text-sm">
        {isEnabled ? (
          <>
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-green-700 font-medium">Ready to download</span>
          </>
        ) : (
          <>
            <Clock className="w-4 h-4 text-orange-500" />
            <span className="text-orange-700">
              {pendingCount} field{pendingCount !== 1 ? "s" : ""} pending validation
            </span>
          </>
        )}
      </div>
    </div>
  )
}
