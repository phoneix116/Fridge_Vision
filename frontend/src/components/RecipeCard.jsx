import React, { useState } from 'react'

const DIFFICULTY = {
  easy:   { label: 'Easy',   bg: '#F0FDF4', color: '#166534' },
  medium: { label: 'Medium', bg: '#FFFBEB', color: '#92400E' },
  hard:   { label: 'Hard',   bg: '#FFF5F5', color: '#991B1B' },
}

function pill(ing) {
  return (typeof ing === 'string' ? ing : ing?.name || '').replace(/_/g, ' ')
}

export default function RecipeCard({ recipe, rank }) {
  const [open, setOpen] = useState(false)
  const pct  = Math.round(recipe.match_percentage || 0)
  const diff = DIFFICULTY[(recipe.difficulty || 'medium').toLowerCase()] || DIFFICULTY.medium
  const barColor = pct >= 75 ? '#4ADE80' : pct >= 50 ? '#FCD34D' : '#D1D5DB'

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{ backgroundColor: '#fff', borderColor: '#E8E4DC' }}
    >
      {/* ── Main row (always visible) ── */}
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full text-left flex items-center gap-3 px-4 py-3 transition-colors hover:bg-stone-50"
      >
        {/* Rank */}
        <span className="text-xs font-black w-5 shrink-0 text-center" style={{ color: '#C8C3BB' }}>
          {rank}
        </span>

        {/* Name + meta */}
        <div className="flex-1 min-w-0">
          <p className="font-bold text-sm leading-snug truncate" style={{ color: '#1C1B1A' }}>
            {recipe.name}
          </p>
          <div className="flex items-center gap-2 mt-0.5">
            <span
              className="text-xs font-bold px-1.5 py-px rounded"
              style={{ backgroundColor: diff.bg, color: diff.color }}
            >
              {diff.label}
            </span>
            {recipe.prep_time_mins && (
              <span className="text-xs" style={{ color: '#9CA3AF' }}>
                {recipe.prep_time_mins} min
              </span>
            )}
            {recipe.servings && (
              <span className="text-xs" style={{ color: '#9CA3AF' }}>
                · {recipe.servings} srv
              </span>
            )}
          </div>
        </div>

        {/* Match % + bar */}
        <div className="shrink-0 flex flex-col items-end gap-1 w-14">
          <span className="text-sm font-black" style={{ color: '#1C1B1A' }}>{pct}%</span>
          <div className="w-full h-1 rounded-full overflow-hidden" style={{ backgroundColor: '#F0EDE6' }}>
            <div
              className="h-full rounded-full"
              style={{ width: `${pct}%`, backgroundColor: barColor }}
            />
          </div>
        </div>

        {/* Chevron */}
        <span className="text-xs shrink-0" style={{ color: '#C8C3BB' }}>
          {open ? '▲' : '▼'}
        </span>
      </button>

      {/* ── Expanded detail ── */}
      {open && (
        <div className="px-4 pb-4 pt-1 border-t space-y-3" style={{ borderColor: '#F0EDE6' }}>
          {/* Ingredient pills */}
          <div className="flex flex-wrap gap-1.5">
            {recipe.matched_ingredients?.map((ing, i) => (
              <span
                key={i}
                className="text-xs font-medium px-2 py-0.5 rounded-full border capitalize"
                style={{ backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', color: '#166534' }}
              >
                {pill(ing)}
              </span>
            ))}
            {recipe.missing_ingredients?.map((ing, i) => (
              <span
                key={i}
                className="text-xs font-medium px-2 py-0.5 rounded-full border capitalize"
                style={{ backgroundColor: '#FAFAF8', borderColor: '#E8E4DC', color: '#9CA3AF' }}
              >
                + {pill(ing)}
              </span>
            ))}
          </div>

          {/* Description */}
          {recipe.description && (
            <p className="text-xs leading-relaxed" style={{ color: '#6B6560' }}>
              {recipe.description}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
