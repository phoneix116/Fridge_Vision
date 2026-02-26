import React, { useState, useCallback } from 'react'
import UploadZone from './components/UploadZone.jsx'
import IngredientGrid from './components/IngredientGrid.jsx'
import RecipeList from './components/RecipeList.jsx'
import LoadingOverlay from './components/LoadingOverlay.jsx'
import { useDetect } from './hooks/useDetect.js'

const STATES = { IDLE: 'idle', UPLOADING: 'uploading', LOADING: 'loading', RESULTS: 'results' }

export default function AppPage({ onBack }) {
  const [appState, setAppState] = useState(STATES.IDLE)
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const { detect, loading, error, results, reset } = useDetect()

  const handleFileSelect = useCallback(file => {
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setAppState(STATES.UPLOADING)
    reset()
  }, [reset])

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setAppState(STATES.LOADING)
    try {
      await detect(selectedFile)
      setAppState(STATES.RESULTS)
    } catch {
      setAppState(STATES.UPLOADING)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setAppState(STATES.IDLE)
    reset()
  }

  const isLoading = appState === STATES.LOADING || loading
  const isResults = appState === STATES.RESULTS && results

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#FAF7F0' }}>
      {isLoading && <LoadingOverlay />}

      {/* ── Top bar ── */}
      <header
        className="flex items-center justify-between px-6 py-4 border-b shrink-0"
        style={{ borderColor: '#E8E4DC', backgroundColor: '#FAF7F0' }}
      >
        <button
          onClick={onBack}
          className="text-sm font-bold transition-opacity hover:opacity-50"
          style={{ color: '#6B6560' }}
        >
          ← Back
        </button>
        <span className="font-black text-base tracking-tight" style={{ color: '#1C1B1A' }}>
          Fridge Vision
        </span>
        <button
          onClick={handleReset}
          disabled={isLoading}
          className="text-sm font-bold transition-opacity hover:opacity-50 disabled:opacity-20"
          style={{ color: '#6B6560' }}
        >
          Reset
        </button>
      </header>

      {/* ── Body ── */}
      {!isResults ? (
        /* ── Upload / idle state ── centered single column */
        <main className="flex-1 flex flex-col justify-center max-w-lg mx-auto w-full px-4 py-10 space-y-3">
          <div className="text-center mb-2">
            <h1 className="font-black text-3xl" style={{ color: '#1C1B1A' }}>
              What's in your fridge?
            </h1>
            <p className="mt-1.5 text-sm font-medium" style={{ color: '#6B6560' }}>
              Upload a photo — we'll detect your ingredients and suggest recipes.
            </p>
          </div>

          <UploadZone
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            previewUrl={previewUrl}
          />

          {appState !== STATES.IDLE && (
            <div className="flex gap-2">
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !selectedFile}
                className="flex-1 py-3.5 rounded-xl font-bold text-sm transition-all duration-150"
                style={
                  isLoading || !selectedFile
                    ? { backgroundColor: '#E8E4DC', color: '#9CA3AF', cursor: 'not-allowed' }
                    : { backgroundColor: '#1C1B1A', color: '#FAF7F0' }
                }
              >
                {isLoading ? 'Analyzing…' : 'Analyze my fridge'}
              </button>
              <button
                onClick={handleReset}
                disabled={isLoading}
                className="px-4 py-3.5 rounded-xl text-sm font-bold transition-all duration-150"
                style={{ backgroundColor: '#F0EDE6', color: '#6B6560' }}
              >
                ✕
              </button>
            </div>
          )}

          {error && (
            <div
              className="rounded-xl px-4 py-3 text-sm font-medium border"
              style={{ backgroundColor: '#FFF5F5', borderColor: '#FECACA', color: '#DC2626' }}
            >
              {error}
            </div>
          )}
        </main>

      ) : (
        /* ── Results state ── two-column layout ── */
        <main className="flex-1 grid grid-cols-1 md:grid-cols-[2fr,3fr] gap-0 overflow-hidden">

          {/* Left panel — photo + ingredients */}
          <div
            className="md:overflow-y-auto px-5 py-6 space-y-4 border-r"
            style={{ borderColor: '#E8E4DC' }}
          >
            {/* Thumbnail */}
            {previewUrl && (
              <div className="rounded-xl overflow-hidden border" style={{ borderColor: '#E8E4DC' }}>
                <img src={previewUrl} alt="Fridge" className="w-full object-cover max-h-52" />
              </div>
            )}

            <IngredientGrid ingredients={results.detected_ingredients} />

            {/* Analyse another */}
            <button
              onClick={handleReset}
              className="w-full py-3 rounded-xl text-sm font-bold border-2 border-dashed transition-all hover:opacity-70"
              style={{ borderColor: '#D4CFC7', color: '#6B6560' }}
            >
              + Try another photo
            </button>
          </div>

          {/* Right panel — categorised recipes */}
          <div className="md:overflow-y-auto px-5 py-6">
            <RecipeList recipes={results.recipes} />
          </div>

        </main>
      )}
    </div>
  )
}
