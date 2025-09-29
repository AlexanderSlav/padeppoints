# 🎾 Tournament Planning Algorithm Documentation

## Overview
The Tournament Planning Algorithm helps organizers determine the optimal tournament configuration based on available resources (courts, time, players). It calculates the maximum points per match that can be played within time constraints while ensuring all players get equal playing time.

## 🧮 Core Algorithm Components

### 1. Tournament Structure Calculation

For Americano format tournaments:
- **Total Rounds** = Number of Players - 1
  - Example: 8 players = 7 rounds
  - This ensures each player plays with different partners throughout

- **Matches per Round** = Number of Players ÷ 4
  - Example: 8 players = 2 matches per round
  - Each match requires exactly 4 players

- **Total Matches** = Total Rounds × Matches per Round
  - Example: 7 rounds × 2 matches = 14 total matches

### 2. Time Estimation Formula

The algorithm calculates tournament duration using:

```
Time per Match = (Points × Seconds per Rally) + Rest Time
Total Time = (Total Matches × Time per Match) ÷ Number of Courts
```

**Parameters:**
- **Points per Match**: Number of points to play (e.g., 24, 32, 36)
- **Seconds per Rally**: Average rally duration (default: 25 seconds)
- **Rest Time**: Break between matches (default: 60 seconds)
- **Court Parallelization**: Multiple courts run matches simultaneously

### 3. Optimal Points Calculation

The algorithm finds the **maximum** points per match that fits within your time constraint:

```python
for points in [48, 44, 40, 36, 32, 28, 24, 20, 16]:
    time_needed = calculate_time(points)
    if time_needed <= available_time:
        return points  # Found maximum that fits!
```

The algorithm tests from high to low, returning the first (highest) value that fits.

## 📊 Step-by-Step Example

### Scenario: 8 Players, 2 Courts, 2 Hours Available

**Step 1: Calculate Tournament Structure**
- Total Rounds: 8 - 1 = 7 rounds
- Matches per Round: 8 ÷ 4 = 2 matches
- Total Matches: 7 × 2 = 14 matches

**Step 2: Calculate Available Time**
- Available: 2 hours = 120 minutes

**Step 3: Find Maximum Points**
Testing different point values:

| Points | Time per Match | Total Time | Fits? |
|--------|---------------|------------|-------|
| 48 | 21 min | 147 min | ❌ Too long |
| 44 | 19.3 min | 135 min | ❌ Too long |
| 40 | 17.7 min | 124 min | ❌ Too long |
| 36 | 16 min | 112 min | ✅ **Fits!** |

**Result:** Maximum 36 points per match

**Step 4: Calculate Final Metrics**
- Total Points: 7 rounds × 2 matches × 36 points = 504 points
- Time Used: 112 minutes (1h 52m)
- Efficiency: 112 ÷ 120 = 93% time utilization
- Time per Round: 112 ÷ 7 = 16 minutes

## 🎯 Efficiency Calculation

Efficiency measures how well you're using available time:

- **Full Tournament Fits**: 
  - Efficiency = (Actual Time Used ÷ Available Time) × 100%
  - Example: 112 minutes used ÷ 120 available = 93%

- **Partial Tournament** (not all rounds fit):
  - Efficiency = 100% (using all available time)
  - Shows how many rounds can be completed

## ⚙️ Customization Parameters

### Seconds per Rally
Adjust based on your playing style:
- **Fast-paced** (10-20 seconds): Quick points, more games
- **Standard** (25 seconds): Default setting
- **Strategic** (30-40 seconds): Longer rallies
- **Endurance** (40+ seconds): Extended play style

### Points per Match
- **Leave empty**: Algorithm finds maximum that fits
- **Set manually**: Override with your preferred value
  - System shows if all rounds can be completed
  - Warns if more time is needed

## 🔄 How Court Parallelization Works

With multiple courts, matches run simultaneously:

**2 Courts, 2 Matches per Round:**
```
Round 1: [Court 1: Match A] [Court 2: Match B] ← Run together
Round 2: [Court 1: Match C] [Court 2: Match D] ← Run together
...
```
Time = 7 rounds × time per match

**1 Court, 2 Matches per Round:**
```
Round 1: [Match A] → [Match B] ← Run sequentially
Round 2: [Match C] → [Match D] ← Run sequentially
...
```
Time = 14 matches × time per match

## 📈 Algorithm Optimization Goals

1. **Maximize Playing Time**: Find highest points that fit
2. **Equal Participation**: All players get same number of matches
3. **Time Efficiency**: Use available time optimally
4. **Flexibility**: Adapt to different court availability

## 💡 Tips for Tournament Organizers

1. **Buffer Time**: Consider adding 10-15% buffer for delays
2. **Rally Duration**: Observe a few games to estimate accurately
3. **Court Availability**: More courts = shorter tournament
4. **Player Count**: Must be divisible by 4 for Americano format

## 🚀 Future Enhancements

- Support for other tournament formats (Mexicano, Round Robin)
- Dynamic adjustment based on match progress
- Historical data integration for better estimates
- Weather/break considerations

---

*This algorithm is continuously refined based on real tournament data and organizer feedback.*