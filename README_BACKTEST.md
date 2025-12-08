# Backtest Performance Feature

## Overview
This feature allows you to backtest the performance of stock recommendations made by the AI investment analysis system and compare them against the NASDAQ index.

## What It Does

The backtest feature:
1. **Compares Portfolio Performance** - Groups stocks by their Ultimate Strength Score (9-10, 8-8.9, 7-7.9, etc.)
2. **Benchmark Against NASDAQ** - Shows how each score group performed vs the NASDAQ index
3. **Analyzes Recommendation Types** - Evaluates performance of "Invest", "Hold", and "Avoid" recommendations
4. **Identifies Best Performers** - Shows top 5 performing stocks in each category

## Key Findings (Oct 2024 - Dec 2025)

### 🏆 Best Performance: Excellent Score Range (9-10)
- **Average Return: +35.94%**
- **Outperformed NASDAQ by +4.30%**
- Top stocks: NVDA (+55.96%), MSFT (+15.93%)

### 📊 NASDAQ Benchmark
- **Total Return: +31.65%**
- Period: October 1, 2024 to December 7, 2025

### 📈 Other Score Ranges
- **Very Good (8-8.9)**: +10.84% average
- **Good (7-7.9)**: +10.83% average
- **Above Average (6-6.9)**: +9.12% average
- **Average and Below (0-5.9)**: -2.33% average

## How to Use

### In Streamlit App:
1. Run the app: `streamlit run app.py`
2. Navigate to "🔬 Backtest Performance" in the sidebar
3. Select your analysis start date (default: Oct 1, 2024)
4. View comprehensive results including:
   - Benchmark performance
   - Score-based portfolio returns
   - Detailed stock-by-stock analysis
   - Key insights and recommendations

### Command Line:
```bash
python backtest_performance.py
```

This will generate a detailed console report with all performance metrics.

## Features

### Interactive Charts
- Bar charts showing returns by score range
- Color-coded performance (green = beat NASDAQ, red = underperformed)
- NASDAQ benchmark line for easy comparison

### Detailed Analysis
- Expandable sections for each score range
- Top 5 performers in each category
- Individual stock returns with start/end prices
- Outperformance vs NASDAQ calculations

### Key Metrics
- Average, best, and worst returns per category
- Number of stocks analyzed
- Comparison against benchmark
- Analysis period duration

## Insights

✅ **What Worked:**
- Highest-rated stocks (9-10) significantly outperformed
- "Excellent" category beat the market by 4.3%
- Top individual stock: +487.58% return

⚠️ **What Didn't:**
- Lower-scored stocks generally underperformed
- Average/Below category had negative returns
- Some variation within score ranges (not all high-scores succeeded)

## Technical Details

### Data Sources
- Stock prices: Yahoo Finance API via yfinance
- Company data: consolidated_company_analysis.json
- Benchmark: NASDAQ Composite (^IXIC)

### Calculation Method
- Equal-weighted portfolio within each score range
- Total return calculation: ((end_price - start_price) / start_price) * 100
- Cached results for 1 hour to improve performance

### Performance
- First run: ~1-2 minutes (fetching all stock data)
- Subsequent runs: Instant (cached)
- Cache TTL: 1 hour

## Files

- `backtest_performance.py` - Core backtesting logic
- `app.py` - Streamlit integration (see `show_backtest_results()`)
- `test_yfinance.py` - API testing utility

## Dependencies

```python
yfinance>=0.2.66
pandas>=2.3.3
plotly>=6.5.0
streamlit>=1.52.1
```

## Future Enhancements

Potential improvements:
- Compare against S&P 500, Dow Jones
- Risk-adjusted returns (Sharpe ratio)
- Sector-specific backtests
- Monthly/quarterly rebalancing simulation
- Transaction cost modeling
- Dividend reinvestment calculations
