const emojiMap = {
  // Fruits
  apple: '🍎',
  banana: '🍌',
  orange: '🍊',
  lemon: '🍋',
  lime: '🍋',
  grape: '🍇',
  strawberry: '🍓',
  blueberry: '🫐',
  raspberry: '🍓',
  watermelon: '🍉',
  pineapple: '🍍',
  mango: '🥭',
  peach: '🍑',
  pear: '🍐',
  cherry: '🍒',
  avocado: '🥑',
  tomato: '🍅',

  // Vegetables
  carrot: '🥕',
  broccoli: '🥦',
  lettuce: '🥬',
  spinach: '🥬',
  kale: '🥬',
  cabbage: '🥬',
  onion: '🧅',
  garlic: '🧄',
  potato: '🥔',
  sweet_potato: '🍠',
  corn: '🌽',
  pepper: '🫑',
  bell_pepper: '🫑',
  cucumber: '🥒',
  zucchini: '🥒',
  eggplant: '🍆',
  mushroom: '🍄',
  celery: '🥬',
  asparagus: '🥦',
  peas: '🫛',
  beans: '🫘',
  green_beans: '🫛',

  // Dairy
  milk: '🥛',
  cheese: '🧀',
  butter: '🧈',
  yogurt: '🥛',
  cream: '🥛',
  egg: '🥚',
  eggs: '🥚',

  // Meat & Protein
  chicken: '🍗',
  beef: '🥩',
  pork: '🥩',
  fish: '🐟',
  salmon: '🐟',
  shrimp: '🦐',
  bacon: '🥓',
  sausage: '🌭',
  ham: '🥩',
  turkey: '🦃',

  // Grains & Baked
  bread: '🍞',
  rice: '🍚',
  pasta: '🍝',
  noodles: '🍜',
  flour: '🌾',
  oats: '🌾',

  // Condiments & Others
  oil: '🫙',
  sauce: '🫙',
  ketchup: '🍅',
  mustard: '🫙',
  mayo: '🫙',
  vinegar: '🫙',
  soy_sauce: '🫙',
  lemon_juice: '🍋',
  sugar: '🍬',
  salt: '🧂',
  pepper_spice: '🌶️',
  herbs: '🌿',
  basil: '🌿',
  parsley: '🌿',
  cilantro: '🌿',
  mint: '🌿',
  ginger: '🫚',
  turmeric: '🟡',
  cumin: '🫙',
  paprika: '🌶️',

  // Beverages
  juice: '🧃',
  water: '💧',
  coffee: '☕',
  tea: '🍵',
  wine: '🍷',
  beer: '🍺',

  // Nuts & Seeds
  almond: '🥜',
  peanut: '🥜',
  walnut: '🥜',
  cashew: '🥜',
  sunflower_seeds: '🌻',

  // Legumes
  lentil: '🫘',
  chickpea: '🫘',
  kidney_bean: '🫘',
  black_bean: '🫘',
  tofu: '🫘',
}

/**
 * Returns an emoji for a given ingredient class name.
 * Falls back to 🥘 if not found.
 */
export function getEmoji(className) {
  if (!className) return '🥘'
  const key = className.toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_')
  return emojiMap[key] || emojiMap[className.toLowerCase()] || '🥘'
}

/**
 * Returns a color category for a given ingredient class name.
 * Used to color-code ingredient chips.
 */
export function getIngredientColor(className) {
  if (!className) return 'gray'
  const key = className.toLowerCase()

  const fruits = ['apple', 'banana', 'orange', 'lemon', 'lime', 'grape', 'strawberry',
    'blueberry', 'raspberry', 'watermelon', 'pineapple', 'mango', 'peach', 'pear',
    'cherry', 'avocado', 'tomato']
  const veggies = ['carrot', 'broccoli', 'lettuce', 'spinach', 'kale', 'cabbage',
    'onion', 'garlic', 'potato', 'sweet_potato', 'corn', 'pepper', 'bell_pepper',
    'cucumber', 'zucchini', 'eggplant', 'mushroom', 'celery', 'asparagus', 'peas', 'beans']
  const dairy = ['milk', 'cheese', 'butter', 'yogurt', 'cream', 'egg', 'eggs']
  const meat = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'bacon',
    'sausage', 'ham', 'turkey']

  if (fruits.some(f => key.includes(f))) return 'orange'
  if (veggies.some(v => key.includes(v))) return 'green'
  if (dairy.some(d => key.includes(d))) return 'yellow'
  if (meat.some(m => key.includes(m))) return 'red'
  return 'purple'
}

export const colorClasses = {
  orange: {
    bg: 'bg-orange-100',
    text: 'text-orange-800',
    border: 'border-orange-300',
    badge: 'bg-orange-200 text-orange-900',
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-300',
    badge: 'bg-green-200 text-green-900',
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-300',
    badge: 'bg-yellow-200 text-yellow-900',
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-300',
    badge: 'bg-red-200 text-red-900',
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-800',
    border: 'border-purple-300',
    badge: 'bg-purple-200 text-purple-900',
  },
}
