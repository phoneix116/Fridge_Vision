import React from 'react'
import { getEmoji } from '../utils/ingredientEmoji.js'

function Chip({ ingredient }) {
  const emoji = getEmoji(ingredient.class_name)
  const name = ingredient.class_name?.replace(/_/g, ' ') || 'Unknown'
  const count = ingredient.count && ingredient.count > 1 ? ingredient.count : null

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-semibold border"
      style={{ backgroundColor: '#fff', borderColor: '#E8E4DC', color: '#1C1B1A' }}
    >
      <span className="text-base leading-none">{emoji}</span>
      <span className="capitalize">{name}</span>
      {count && (
        <span
          className="text-xs font-black rounded-full px-1.5 py-0.5 leading-none"
          style={{ backgroundColor: '#F0EDE6', color: '#6B6560' }}
        >
          ×{count}
        </span>
      )}
    </span>
  )
}

export default function IngredientGrid({ ingredients }) {
  return (
    <div
      className="rounded-2xl border p-5"
      style={{ backgroundColor: '#fff', borderColor: '#E8E4DC' }}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-sm" style={{ color: '#1C1B1A' }}>Detected ingredients</h2>
        {ingredients?.length > 0 && (
          <span
            className="text-xs font-bold rounded-full px-2.5 py-1"
            style={{ backgroundColor: '#F0EDE6', color: '#6B6560' }}
          >
            {ingredients.length} found
          </span>
        )}
      </div>

      {ingredients && ingredients.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {ingredients.map((ing, i) => (
            <Chip key={`${ing.class_name}-${i}`} ingredient={ing} />
          ))}
        </div>
      ) : (
        <p className="text-sm" style={{ color: '#9CA3AF' }}>
          No ingredients detected — try a clearer photo with better lighting.
        </p>
      )}
    </div>
  )
}
