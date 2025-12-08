"""
Analyze which sector-score combinations beat NASDAQ
"""
from backtest_performance import PortfolioBacktest

# Create backtester
backtester = PortfolioBacktest(start_date='2024-12-01')

# Load data
data, combined_df = backtester.load_company_data()

# Get NASDAQ return
nasdaq = backtester.get_nasdaq_returns()
nasdaq_return = nasdaq['return_pct'] if nasdaq else 0

print("=" * 80)
print(f"NASDAQ Return: {nasdaq_return:+.2f}%")
print("=" * 80)

# Get sector-score performance
sector_results = backtester.calculate_sector_score_performance(data, combined_df)

# Find winners (sectors that beat NASDAQ)
winners = []
for key, result in sector_results.items():
    if result['avg_return'] > nasdaq_return:
        winners.append({
            'sector_score': key,
            'avg_return': result['avg_return'],
            'num_stocks': result['num_stocks'],
            'outperformance': result['avg_return'] - nasdaq_return,
            'stocks': result['stocks']
        })

# Sort by outperformance
winners.sort(key=lambda x: x['outperformance'], reverse=True)

print(f"\n\n🏆 SECTORS THAT BEAT NASDAQ (Found {len(winners)} winning combinations)")
print("=" * 80)

for i, winner in enumerate(winners, 1):
    print(f"\n{i}. {winner['sector_score']}")
    print(f"   Average Return: {winner['avg_return']:+.2f}%")
    print(f"   Outperformance: {winner['outperformance']:+.2f}%")
    print(f"   Number of Stocks: {winner['num_stocks']}")
    print(f"   Stocks:")
    for stock in winner['stocks']:
        print(f"      {stock['symbol']:6s} - {stock['name'][:40]:40s} {stock['return_pct']:+7.2f}%")

# Also check score ranges
print("\n\n📊 PERFORMANCE BY SCORE RANGE")
print("=" * 80)
score_results = backtester.calculate_portfolio_by_score(data, combined_df)

for label, results in score_results.items():
    beat_nasdaq = "✅ BEAT NASDAQ" if results['avg_return'] > nasdaq_return else "❌ Lost to NASDAQ"
    print(f"\n{label}: {results['avg_return']:+.2f}% {beat_nasdaq}")
    print(f"   vs NASDAQ: {results['avg_return'] - nasdaq_return:+.2f}%")
    print(f"   Stocks: {results['num_stocks']}/{results['total_companies']}")

print("\n" + "=" * 80)
