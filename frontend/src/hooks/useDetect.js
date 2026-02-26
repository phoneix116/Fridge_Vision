import { useState } from 'react'

export function useDetect() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)

  async function detect(imageFile, options = {}) {
    setLoading(true)
    setError(null)
    setResults(null)

    const {
      useLlm = true,
      topK = 5,
      enableOcr = false,
      confidenceThreshold = 0.25,
    } = options

    const params = new URLSearchParams({
      use_llm: useLlm,
      top_k: topK,
      enable_ocr: enableOcr,
      confidence_threshold: confidenceThreshold,
    })

    const formData = new FormData()
    formData.append('image', imageFile)

    try {
      const response = await fetch(`/api/detect-and-recommend?${params}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errBody = await response.text()
        throw new Error(`API error ${response.status}: ${errBody}`)
      }

      const data = await response.json()
      setResults(data)
      return data
    } catch (err) {
      setError(err.message || 'Something went wrong')
      throw err
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setResults(null)
    setError(null)
    setLoading(false)
  }

  return { detect, loading, error, results, reset }
}
