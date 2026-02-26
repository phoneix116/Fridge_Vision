import React from 'react'
import RecipeCard from './RecipeCard.jsx'

const TIERS = [
  {
    key: 'great',
    label: 'Great match',
    range: '≥ 75%',
    dot: '#4ADE80',
    test: r => r.match_percentage >= 75,
  },
  {
    key: 'good',
    label: 'Good match',
    range: '50 – 74%',
    dot: '#FCD34D',
    test: r => r.match_percentage >= 50 && r.match_percentage < 75,
  },
  {
    key: 'partial',
    label: 'Partial match',
    range: '< 50%',
    dot: '#D1D5DB',
    test: r => r.match_percentage < 50,
  },
]

export default function RecipeList({ recipes }) {
  if (!recipes || recipes.length === 0) {
    return (
      <div className="flex items-center justify-center h-40">
        <p className="text-sm font-medium" style={{ color: '#9CA3AF' }}>
          No recipes found for these ingredients.
        </p>
      </div>
    )
  }

  // rank is the global position across all tiers
  let globalRank = 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="font-black text-base" style={{ color: '#1C1B1A' }}>Recipe suggestions</h2>
        <span
          className="text-xs font-bold rounded-full px-2.5 py-1"
          style={{ backgroundColor: '#F0EDE6', color: '#6B6560' }}
        >
          {recipes.length} found
        </span>
      </div>

      {TIERS.map(tier => {
        const group = recipes.filter(tier.test)
        if (group.length === 0) return null
        return (
          <div key={tier.key}>
            {/* Tier header */}
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: tier.dot }} />
              <span className="font-black text-xs uppercase tracking-widest" style={{ color: '#1C1B1A' }}>
                {tier.label}
              </span>
              <span className="text-xs font-medium" style={{ color: '#9CA3AF' }}>
                {tier.range}
              </span>
              <span
                className="ml-auto text-xs font-bold rounded-full px-2 py-0.5"
                style={{ backgroundColor: '#F0EDE6', color: '#6B6560' }}
              >
                {group.length}
              </span>
            </div>

            <div className="space-y-2">
              {group.map(recipe => {
                globalRank++
                return (
                  <RecipeCard
                    key={`${recipe.name}-${globalRank}`}
                    recipe={recipe}
                    rank={globalRank}
                  />
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
