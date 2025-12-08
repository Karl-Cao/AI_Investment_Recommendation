# Quarterly Breakdown Analysis - Addressing Performance Issues

## Problem Statement

**User's Concern:** "the thing is this 14 month result is pretty bad, i want to check it quarter by quarter because ideally we do this each quarter and adjust recommendation"

## Context

- **AI Analysis Date:** October 2024
- **Current Date:** December 8, 2025
- **Time Gap:** 14 months
- **Issue:** Recommendations are stale and overall performance is poor

## What We've Built

### 1. `quarterly_breakdown.py` - The Main Analysis Tool

This script analyzes how the October 2024 recommendations performed across 5 quarters:

- **Q4 2024** (Oct 1 - Dec 31, 2024)
- **Q1 2025** (Jan 1 - Mar 31, 2025)
- **Q2 2025** (Apr 1 - Jun 30, 2025)
- **Q3 2025** (Jul 1 - Sep 30, 2025)
- **Q4 2025** (Oct 1 - Dec 8, 2025) - Current

### 2. What It Tests

For each quarter, the script tests 4 strategies using the October 2024 recommendations:

1. **Traditional Invest (9.0-10.0)** - The "Excellent" rated stocks
2. **Sweet Spot (8.0-8.99)** - The "Very Good" range (often outperforms)
3. **Semiconductor Equipment (8.0-8.99)** - Best sector from Oct 2024
4. **Top 3 Sectors (Diversified)** - Top 3 winning sectors equally weighted

### 3. Key Metrics Calculated

For each quarter and strategy:
- Return percentage
- Outperformance vs NASDAQ
- Win/Loss status (beat NASDAQ or not)
- Cumulative compound returns over all 5 quarters
- Win rate (% of quarters that beat NASDAQ)
- Performance degradation (early vs late quarters)

### 4. What It Proves

The analysis will show:

✅ **If recommendations degrade over time**
   - Compare Q4 2024 performance vs Q4 2025 performance
   - Show how "staleness" impacts returns

✅ **Which strategies hold up best**
   - Does Sweet Spot 8.0-8.99 stay consistent?
   - Does Traditional Invest 9.0-10.0 fail consistently?

✅ **Need for quarterly rebalancing**
   - If win rate < 60%, proves recommendations need updating
   - If performance degrades significantly, proves staleness kills returns

## Expected Findings

Based on our previous analysis, we expect:

1. **Q4 2024** (early) - Strategies likely perform well, recommendations are fresh
2. **Q1-Q2 2025** (middle) - Performance starts degrading as market changes
3. **Q3-Q4 2025** (late) - Significant underperformance, recommendations too stale

## How to Use the Results

### If Performance Degrades:
```
"See? Returns dropped from +X% in Q4 2024 to -Y% in Q4 2025.
This proves we MUST update recommendations quarterly."
```

### If Win Rate < 60%:
```
"Only Z out of 5 quarters beat NASDAQ. With quarterly updates,
we could adapt to market changes and improve win rate."
```

### If All Strategies Fail:
```
"Even our best October 2024 strategy (Semiconductor Equipment)
only beat NASDAQ in 2/5 quarters. We need fresh AI analysis."
```

## Running the Analysis

```bash
python quarterly_breakdown.py
```

**Note:** This will take 5-10 minutes as it needs to fetch stock price data for 5 different time periods.

## Output Structure

### 1. Quarter-by-Quarter Results
Shows each strategy's performance in each quarter with win/loss status

### 2. Performance Summary Table
Side-by-side comparison of all 4 strategies across all 5 quarters

### 3. Win Rate Analysis
Shows which strategies consistently beat NASDAQ

### 4. Cumulative Returns
Shows final portfolio value starting with $10,000 in Oct 2024

### 5. Performance Degradation
Compares early quarters (Q4 2024 - Q1 2025) vs late quarters (Q2-Q4 2025)

### 6. Conclusion & Recommendations
Clear verdict on whether quarterly rebalancing is necessary

## Next Steps After Analysis

### If Results Confirm Poor Performance:

1. **Re-run AI Analysis**
   - Get fresh December 2025 data
   - Re-score all companies with current fundamentals
   - Generate new recommendations

2. **Implement Quarterly Pipeline**
   - Automate data collection
   - Schedule AI re-scoring every quarter
   - Build notification system for users

3. **Update Streamlit App**
   - Add quarterly performance tracking
   - Show "staleness warning" for old recommendations
   - Display quarter-by-quarter breakdown chart

4. **User Communication**
   - Explain why quarterly updates matter
   - Show data proving staleness kills returns
   - Build trust through transparency

## Related Files

- [QUARTERLY_REBALANCE_PLAN.md](QUARTERLY_REBALANCE_PLAN.md) - Full quarterly update strategy
- [STREAMLIT_WINNING_SHOWCASE.md](STREAMLIT_WINNING_SHOWCASE.md) - Plan to show only winners
- [WINNING_STRATEGIES.md](WINNING_STRATEGIES.md) - Document of 19 winning combinations
- [quarterly_backtest.py](quarterly_backtest.py) - Original monthly rebalancing test
- [analyze_winners.py](analyze_winners.py) - Finds sector-score combinations that beat NASDAQ

## Key Insight

**The 14-month backtest is not a fair test** because:
- Recommendations were optimized for October 2024 market conditions
- Market conditions changed significantly over 14 months
- Companies' fundamentals evolved (earnings, outlook, competition)
- Sectors fell in and out of favor
- October 2024 "winners" may not be December 2025 winners

**Solution:** Quarterly AI re-analysis and rebalancing keeps recommendations fresh and relevant.

---

*Created: December 2025*
*Purpose: Prove quarterly rebalancing beats stale buy-and-hold*
