export const ratingRanges = [
  { min: 1000, max: 1099, level: 'Beginner', color: '#A5D6A7', playtomic: '1.0', description: 'No experience, just starting to play' },
  { min: 1100, max: 1199, level: 'Novice', color: '#81C784', playtomic: '2.0', description: 'Consistent at a low pace' },
  { min: 1200, max: 1299, level: 'Improver', color: '#66BB6A', playtomic: '2.5', description: 'Consistent at medium pace, shots lack direction' },
  { min: 1300, max: 1399, level: 'Weak Intermediate', color: '#9CCC65', playtomic: '3.0', description: 'Building confidence with shorts, consistent at medium pace' },
  { min: 1400, max: 1499, level: 'Intermediate', color: '#FFEB3B', playtomic: '3.5', description: 'Has control and pace, previous racquet skills' },
  { min: 1500, max: 1599, level: 'Strong Intermediate', color: '#FFC107', playtomic: '4.0', description: 'Experience constructing padel points, consistent player' },
  { min: 1600, max: 1699, level: 'Weak Advanced', color: '#FF9800', playtomic: '4.5', description: 'Resourceful - executing winners, ability to force errors' },
  { min: 1700, max: 1799, level: 'Advanced', color: '#F57C00', playtomic: '5.0', description: 'Experience competing at tournament level' },
  { min: 1800, max: 1899, level: 'Strong Advanced', color: '#EF5350', playtomic: '5.5', description: 'Top nationally ranked player, regular tournament competitor' },
  { min: 1900, max: 1999, level: 'Weak Expert', color: '#E53935', playtomic: '6.0', description: 'Semi-professional, World ranking outside top 250' },
  { min: 2000, max: 9999, level: 'Expert', color: '#B71C1C', playtomic: '6.5+', description: 'Professional player, World ranking potential' }
];

export const getRatingColor = (rating) => {
  const range = ratingRanges.find(r => rating >= r.min && rating <= r.max);
  return range ? range.color : '#718096';
};

export const getRatingLevel = (rating) => {
  const range = ratingRanges.find(r => rating >= r.min && rating <= r.max);
  return range ? range.level : 'Unranked';
};

export const getRatingInfo = (rating) => {
  return ratingRanges.find(r => rating >= r.min && rating <= r.max) || null;
};

// Determine if text should be dark on light backgrounds
export const getTextColorForRating = (rating) => {
  const range = ratingRanges.find(r => rating >= r.min && rating <= r.max);
  if (!range) return 'white';

  // Use dark text for yellow/light colors (Intermediate and Strong Intermediate)
  const lightBackgrounds = ['#FFEB3B', '#FFC107', '#9CCC65'];
  return lightBackgrounds.includes(range.color) ? '#1a202c' : 'white';
};