import React, { useCallback, useRef, useState } from 'react'

export default function UploadZone({ onFileSelect, selectedFile, previewUrl }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = useCallback(e => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith('image/')) onFileSelect(file)
  }, [onFileSelect])

  const handleChange = e => {
    const file = e.target.files?.[0]
    if (file) onFileSelect(file)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onClick={() => !previewUrl && inputRef.current?.click()}
      className="relative rounded-2xl border-2 overflow-hidden transition-all duration-150"
      style={
        previewUrl
          ? { borderColor: '#E8E4DC', borderStyle: 'solid', backgroundColor: '#fff', cursor: 'default' }
          : dragging
            ? { borderColor: '#1C1B1A', borderStyle: 'dashed', backgroundColor: '#F0EDE6', cursor: 'pointer' }
            : { borderColor: '#D4CFC7', borderStyle: 'dashed', backgroundColor: '#fff', cursor: 'pointer' }
      }
    >
      <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={handleChange} />

      {previewUrl ? (
        <div>
          <img src={previewUrl} alt="Fridge preview" className="w-full max-h-72 object-cover" />
          <div
            className="flex items-center justify-between px-4 py-2.5 border-t"
            style={{ backgroundColor: '#FAF7F0', borderColor: '#E8E4DC' }}
          >
            <span className="text-sm truncate" style={{ color: '#6B6560' }}>{selectedFile?.name}</span>
            <button
              onClick={e => { e.stopPropagation(); inputRef.current?.click() }}
              className="text-xs font-bold ml-3 shrink-0 transition-opacity hover:opacity-60"
              style={{ color: '#1C1B1A' }}
            >
              Change
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 py-14 px-8 text-center">
          <span className={`text-4xl transition-transform duration-150 ${dragging ? 'scale-110' : ''}`}>
            📷
          </span>
          <div>
            <p className="font-bold text-sm" style={{ color: '#1C1B1A' }}>
              {dragging ? 'Drop it here' : 'Drop a photo of your fridge'}
            </p>
            <p className="text-sm mt-1" style={{ color: '#9CA3AF' }}>
              or <span className="underline underline-offset-2" style={{ color: '#6B6560' }}>browse files</span>
            </p>
          </div>
          <p className="text-xs" style={{ color: '#C8C3BB' }}>JPG · PNG · WEBP</p>
        </div>
      )}
    </div>
  )
}
