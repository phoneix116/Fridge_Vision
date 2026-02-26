import React from 'react'

/* ─────────────── static mock data for the demo strip ─────────────── */
const DEMO_INGREDIENTS = [
  { emoji: '🍅', name: 'Tomato',  count: 4 },
  { emoji: '🥕', name: 'Carrot',  count: 2 },
  { emoji: '🥬', name: 'Cabbage', count: null },
  { emoji: '🥚', name: 'Egg',     count: 6 },
  { emoji: '🧀', name: 'Cheese',  count: null },
  { emoji: '🧄', name: 'Garlic',  count: 3 },
]

const DEMO_RECIPE = {
  name: 'Tomato & Egg Stir Fry',
  difficulty: 'Easy',
  time: '15 min',
  servings: 2,
  match: 92,
  matched: ['Tomato', 'Egg', 'Garlic'],
  missing: ['Spring onion'],
}

/* ─────────────── feature cards ─────────────── */
const FEATURES = [
  {
    icon: '🎯',
    title: 'Instant Detection',
    desc: 'YOLOv8 computer vision spots every item in your fridge — produce, dairy, meat, and more.',
  },
  {
    icon: '🍽️',
    title: 'Smart Recipe Matching',
    desc: 'Recipes are ranked by how many ingredients you already have on hand, not what you need to buy.',
  },
  {
    icon: '♻️',
    title: 'Cut Food Waste',
    desc: 'Stop letting things expire. Cook with what\'s there and discover meals you\'d never think of.',
  },
]

/* ─────────────── steps ─────────────── */
const STEPS = [
  { n: '01', title: 'Photograph',  desc: 'Open your fridge and take a photo, or upload an existing one.' },
  { n: '02', title: 'Detect',      desc: 'Our AI scans the image and identifies every visible ingredient.' },
  { n: '03', title: 'Cook',        desc: 'Browse recipes sorted by how well they match what you have.' },
]

/* ═══════════════════════════════════════════════════════════════════ */

export default function Landing({ onStart }) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF7F0' }}>

      {/* ── Nav ── */}
      <nav className="flex items-center justify-between px-6 sm:px-12 py-6 max-w-6xl mx-auto">
        <span className="font-black text-xl tracking-tight" style={{ color: '#1C1B1A' }}>
          Fridge Vision
        </span>
        <button
          onClick={onStart}
          className="text-sm font-bold px-5 py-2.5 rounded-full border-2 transition-all duration-150 hover:scale-105"
          style={{ borderColor: '#1C1B1A', color: '#1C1B1A' }}
        >
          Open app →
        </button>
      </nav>

      {/* ── Hero ── */}
      <section className="px-6 sm:px-12 pt-12 pb-20 max-w-6xl mx-auto">
        <div className="max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.3em] mb-6" style={{ color: '#6B6560' }}>
            AI-Powered Kitchen Assistant
          </p>

          <h1
            className="font-black leading-[1.05] mb-6"
            style={{ fontSize: 'clamp(3rem, 8vw, 5.5rem)', color: '#1C1B1A' }}
          >
            Know what's in<br />
            your fridge.<br />
            <span style={{ color: '#2C5F2E' }}>Cook something great.</span>
          </h1>

          <p className="text-lg font-medium mb-10 max-w-xl leading-relaxed" style={{ color: '#6B6560' }}>
            Fridge Vision uses computer vision to identify your ingredients
            and instantly suggest recipes — no typing, no searching.
          </p>

          <button
            onClick={onStart}
            className="inline-flex items-center gap-2 font-bold text-base px-8 py-4 rounded-full transition-all duration-150 hover:scale-105 hover:shadow-lg"
            style={{ backgroundColor: '#1C1B1A', color: '#FAF7F0' }}
          >
            Get started — it's free
            <span className="text-xl">→</span>
          </button>
        </div>
      </section>

      {/* ── Demo preview strip ── */}
      <section className="px-6 sm:px-12 pb-24 max-w-6xl mx-auto">
        <div
          className="rounded-3xl p-6 sm:p-8 border"
          style={{ backgroundColor: '#fff', borderColor: '#E8E4DC' }}
        >
          {/* label */}
          <p className="text-xs font-bold uppercase tracking-widest mb-6" style={{ color: '#6B6560' }}>
            Sample output
          </p>

          {/* Ingredient row */}
          <div className="mb-6">
            <p className="text-xs font-bold mb-3" style={{ color: '#6B6560' }}>
              Detected ingredients · 6 found
            </p>
            <div className="flex flex-wrap gap-2">
              {DEMO_INGREDIENTS.map(ing => (
                <span
                  key={ing.name}
                  className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-semibold border"
                  style={{ backgroundColor: '#FAF7F0', borderColor: '#E8E4DC', color: '#1C1B1A' }}
                >
                  <span>{ing.emoji}</span>
                  <span>{ing.name}</span>
                  {ing.count && (
                    <span
                      className="text-xs font-black rounded-full px-1.5 py-0.5 leading-none"
                      style={{ backgroundColor: '#E8E4DC', color: '#6B6560' }}
                    >
                      ×{ing.count}
                    </span>
                  )}
                </span>
              ))}
            </div>
          </div>

          {/* Recipe card mock */}
          <div
            className="rounded-2xl border overflow-hidden"
            style={{ borderColor: '#E8E4DC' }}
          >
            <div className="flex items-start gap-4 p-5 pb-4">
              <span className="text-xs font-black mt-0.5 w-5 shrink-0" style={{ color: '#C8C3BB' }}>#1</span>
              <div className="flex-1">
                <p className="font-bold text-base" style={{ color: '#1C1B1A' }}>{DEMO_RECIPE.name}</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: '#DCFCE7', color: '#166534' }}>
                    {DEMO_RECIPE.difficulty}
                  </span>
                  <span className="text-xs font-medium" style={{ color: '#6B6560' }}>{DEMO_RECIPE.time}</span>
                  <span className="text-xs font-medium" style={{ color: '#6B6560' }}>{DEMO_RECIPE.servings} servings</span>
                </div>
              </div>
              <div className="text-right shrink-0">
                <p className="text-2xl font-black" style={{ color: '#1C1B1A' }}>{DEMO_RECIPE.match}%</p>
                <p className="text-xs" style={{ color: '#6B6560' }}>match</p>
              </div>
            </div>
            <div className="px-5 pb-4">
              <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: '#F5F0E8' }}>
                <div className="h-full rounded-full" style={{ width: `${DEMO_RECIPE.match}%`, backgroundColor: '#4ADE80' }} />
              </div>
            </div>
            <div className="px-5 pb-5 flex flex-wrap gap-1.5">
              {DEMO_RECIPE.matched.map(i => (
                <span key={i} className="text-xs font-medium px-2 py-0.5 rounded-full border" style={{ backgroundColor: '#F0FDF4', borderColor: '#BBF7D0', color: '#166534' }}>{i}</span>
              ))}
              {DEMO_RECIPE.missing.map(i => (
                <span key={i} className="text-xs font-medium px-2 py-0.5 rounded-full border" style={{ backgroundColor: '#FAFAF8', borderColor: '#E8E4DC', color: '#9CA3AF' }}>+ {i}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="px-6 sm:px-12 py-20 border-t" style={{ borderColor: '#E8E4DC' }}>
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#6B6560' }}>
            Why Fridge Vision
          </p>
          <h2 className="font-black text-3xl sm:text-4xl mb-12" style={{ color: '#1C1B1A' }}>
            Less guessing.<br />More cooking.
          </h2>

          <div className="grid sm:grid-cols-3 gap-6">
            {FEATURES.map(f => (
              <div
                key={f.title}
                className="rounded-2xl p-6 border"
                style={{ backgroundColor: '#fff', borderColor: '#E8E4DC' }}
              >
                <span className="text-3xl block mb-4">{f.icon}</span>
                <h3 className="font-black text-lg mb-2" style={{ color: '#1C1B1A' }}>{f.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#6B6560' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="px-6 sm:px-12 py-20 border-t" style={{ borderColor: '#E8E4DC' }}>
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#6B6560' }}>
            How it works
          </p>
          <h2 className="font-black text-3xl sm:text-4xl mb-12" style={{ color: '#1C1B1A' }}>
            Three steps.<br />That's it.
          </h2>

          <div className="grid sm:grid-cols-3 gap-10">
            {STEPS.map(s => (
              <div key={s.n}>
                <p className="font-black text-5xl mb-4" style={{ color: '#E8E4DC' }}>{s.n}</p>
                <h3 className="font-black text-xl mb-2" style={{ color: '#1C1B1A' }}>{s.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#6B6560' }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer CTA ── */}
      <section className="px-6 sm:px-12 py-24 border-t text-center" style={{ borderColor: '#E8E4DC' }}>
        <h2 className="font-black text-4xl sm:text-5xl mb-4" style={{ color: '#1C1B1A' }}>
          Ready to cook?
        </h2>
        <p className="mb-8 text-base font-medium" style={{ color: '#6B6560' }}>
          Upload a photo and get recipe ideas in under 10 seconds.
        </p>
        <button
          onClick={onStart}
          className="inline-flex items-center gap-2 font-bold text-base px-8 py-4 rounded-full transition-all duration-150 hover:scale-105 hover:shadow-lg"
          style={{ backgroundColor: '#1C1B1A', color: '#FAF7F0' }}
        >
          Try Fridge Vision →
        </button>
      </section>

      {/* ── Footer ── */}
      <footer className="px-6 sm:px-12 py-6 border-t flex items-center justify-between max-w-6xl mx-auto" style={{ borderColor: '#E8E4DC' }}>
        <span className="font-black text-sm" style={{ color: '#1C1B1A' }}>Fridge Vision</span>
        <span className="text-xs" style={{ color: '#C8C3BB' }}>Powered by YOLOv8 · LLM recipe matching</span>
      </footer>

    </div>
  )
}
