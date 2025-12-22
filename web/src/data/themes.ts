export interface Theme {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  description: string;
}

export const themes: Theme[] = [
  {
    name: 'Ocean Blue',
    primary: 'from-blue-500 to-blue-600',
    secondary: 'from-slate-50 to-blue-50',
    accent: 'from-green-400 to-green-500',
    background: 'bg-gradient-to-br from-slate-50 to-blue-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Cool and professional with ocean-inspired blues'
  },
  {
    name: 'Sunset Orange',
    primary: 'from-orange-500 to-red-500',
    secondary: 'from-orange-50 to-red-50',
    accent: 'from-yellow-400 to-orange-400',
    background: 'bg-gradient-to-br from-orange-50 to-red-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Energetic and motivating with warm sunset colors'
  },
  {
    name: 'Forest Green',
    primary: 'from-green-600 to-emerald-600',
    secondary: 'from-green-50 to-emerald-50',
    accent: 'from-lime-400 to-green-400',
    background: 'bg-gradient-to-br from-green-50 to-emerald-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Natural and calming with forest-inspired greens'
  },
  {
    name: 'Purple Gradient',
    primary: 'from-purple-500 to-indigo-600',
    secondary: 'from-purple-50 to-indigo-50',
    accent: 'from-pink-400 to-purple-400',
    background: 'bg-gradient-to-br from-purple-50 to-indigo-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Modern and creative with purple gradients'
  },
  {
    name: 'Dark Mode',
    primary: 'from-blue-400 to-blue-500',
    secondary: 'from-slate-900 to-slate-800',
    accent: 'from-green-400 to-emerald-400',
    background: 'bg-gradient-to-br from-slate-900 to-slate-800',
    surface: 'bg-slate-800/80',
    text: 'text-white',
    description: 'Sleek dark theme for low-light environments'
  }
];
