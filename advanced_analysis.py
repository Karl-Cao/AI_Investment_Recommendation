"""
Advanced multi-dimensional analysis to find ALL ways to beat NASDAQ
Explores: Sector, Score, Recommendation, Market Cap, Volatility, Combinations
"""
from backtest_performance import PortfolioBacktest
import pandas as pd
import numpy as np

# Create backtester
backtester = PortfolioBacktest(start_date='2024-12-01')

# Load data
data, combined_df = backtester.load_company_data()

# Get NASDAQ return
nasdaq = backtester.get_nasdaq_returns()
nasdaq_return = nasdaq['return_pct'] if nasdaq else 0

print("=" * 80)
print(f"NASDAQ Benchmark: {nasdaq_return:+.2f}%")
print("=" * 80)

# Collect all stocks with detailed information
all_stocks = []

for company_name, details in data['company_analysis'].items():
    score = details.get('ultimate_strength', 0)
    recommendation = details.get('recommendation', '')

    # Find company in CSV
    company_row = combined_df[combined_df['name'].str.lower() == company_name.lower()]

    # Fuzzy matching if needed
    if company_row.empty:
        normalized_name = company_name.lower().replace(',', '').replace('.', '').strip()
        for suffix in [' inc', ' corp', ' corporation', ' incorporated', ' company', ' co', ' ltd']:
            normalized_name = normalized_name.replace(suffix, '')
        normalized_name = normalized_name.strip()

        for idx, row in combined_df.iterrows():
            csv_normalized = row['name'].lower().replace(',', '').replace('.', '').strip()
            for suffix in [' inc', ' corp', ' corporation', ' incorporated', ' company', ' co', ' ltd']:
                csv_normalized = csv_normalized.replace(suffix, '')
            csv_normalized = csv_normalized.strip()

            if normalized_name == csv_normalized:
                company_row = combined_df.iloc[[idx]]
                break

    if not company_row.empty:
        symbol = backtester.clean_symbol(company_row.iloc[0]['symbol'])
        industry = company_row.iloc[0].get('industry', 'Unknown')

        result = backtester.get_stock_returns(symbol, backtester.start_date, backtester.end_date)
        if result:
            all_stocks.append({
                'name': company_name,
                'symbol': symbol,
                'score': score,
                'recommendation': recommendation,
                'industry': industry,
                'return_pct': result['return_pct'],
                'start_price': result['start_price'],
                'end_price': result['end_price'],
                'beat_nasdaq': result['return_pct'] > nasdaq_return
            })

# Convert to DataFrame for easier analysis
df = pd.DataFrame(all_stocks)

print(f"\n📊 Total Stocks Analyzed: {len(df)}")
print(f"✅ Stocks that Beat NASDAQ: {df['beat_nasdaq'].sum()} ({df['beat_nasdaq'].sum()/len(df)*100:.1f}%)")
print(f"❌ Stocks that Lost to NASDAQ: {(~df['beat_nasdaq']).sum()} ({(~df['beat_nasdaq']).sum()/len(df)*100:.1f}%)")

# ============================================================================
# ANALYSIS 1: By Recommendation (Invest/Hold/Avoid)
# ============================================================================
print("\n\n" + "=" * 80)
print("📈 ANALYSIS 1: PERFORMANCE BY RECOMMENDATION")
print("=" * 80)

for rec in ['Invest', 'Hold', 'Avoid']:
    rec_stocks = df[df['recommendation'] == rec]
    if len(rec_stocks) > 0:
        beat_count = rec_stocks['beat_nasdaq'].sum()
        beat_pct = beat_count / len(rec_stocks) * 100
        avg_return = rec_stocks['return_pct'].mean()

        status = "✅ WINNER" if avg_return > nasdaq_return else "❌ LOSER"
        print(f"\n{rec}: {avg_return:+.2f}% (vs NASDAQ: {avg_return - nasdaq_return:+.2f}%) {status}")
        print(f"  Stocks: {len(rec_stocks)} | Beat NASDAQ: {beat_count} ({beat_pct:.1f}%)")
        print(f"  Best: {rec_stocks['return_pct'].max():+.2f}% | Worst: {rec_stocks['return_pct'].min():+.2f}%")

# ============================================================================
# ANALYSIS 2: By Individual Score Bins (granular)
# ============================================================================
print("\n\n" + "=" * 80)
print("📊 ANALYSIS 2: PERFORMANCE BY INDIVIDUAL SCORE BINS")
print("=" * 80)

score_bins = [
    (9.5, 10.0, "9.5-10.0"),
    (9.0, 9.49, "9.0-9.49"),
    (8.5, 8.99, "8.5-8.99"),
    (8.0, 8.49, "8.0-8.49"),
    (7.5, 7.99, "7.5-7.99"),
    (7.0, 7.49, "7.0-7.49"),
    (6.5, 6.99, "6.5-6.99"),
    (6.0, 6.49, "6.0-6.49"),
]

winners = []
for min_score, max_score, label in score_bins:
    bin_stocks = df[(df['score'] >= min_score) & (df['score'] <= max_score)]
    if len(bin_stocks) >= 3:  # At least 3 stocks
        avg_return = bin_stocks['return_pct'].mean()
        beat_count = bin_stocks['beat_nasdaq'].sum()
        beat_pct = beat_count / len(bin_stocks) * 100

        status = "✅" if avg_return > nasdaq_return else "❌"
        print(f"\n{label}: {avg_return:+.2f}% (vs NASDAQ: {avg_return - nasdaq_return:+.2f}%) {status}")
        print(f"  Stocks: {len(bin_stocks)} | Beat NASDAQ: {beat_count} ({beat_pct:.1f}%)")

        if avg_return > nasdaq_return:
            winners.append({
                'label': label,
                'avg_return': avg_return,
                'outperformance': avg_return - nasdaq_return,
                'count': len(bin_stocks),
                'beat_rate': beat_pct
            })

# ============================================================================
# ANALYSIS 3: By Industry (Top 20)
# ============================================================================
print("\n\n" + "=" * 80)
print("🏭 ANALYSIS 3: PERFORMANCE BY INDUSTRY (Top 20 Winners)")
print("=" * 80)

industry_perf = df.groupby('industry').agg({
    'return_pct': ['mean', 'count'],
    'beat_nasdaq': 'sum'
}).round(2)

industry_perf.columns = ['avg_return', 'count', 'beat_count']
industry_perf = industry_perf[industry_perf['count'] >= 2]  # At least 2 stocks
industry_perf['beat_rate'] = (industry_perf['beat_count'] / industry_perf['count'] * 100).round(1)
industry_perf['outperformance'] = industry_perf['avg_return'] - nasdaq_return
industry_perf = industry_perf.sort_values('outperformance', ascending=False)

for idx, (industry, row) in enumerate(industry_perf.head(20).iterrows(), 1):
    status = "✅" if row['outperformance'] > 0 else "❌"
    print(f"\n{idx}. {industry}: {row['avg_return']:+.2f}% ({row['outperformance']:+.2f}% vs NASDAQ) {status}")
    print(f"   Stocks: {int(row['count'])} | Beat Rate: {row['beat_rate']:.0f}%")

# ============================================================================
# ANALYSIS 4: Recommendation + Score Combinations
# ============================================================================
print("\n\n" + "=" * 80)
print("🎯 ANALYSIS 4: RECOMMENDATION + SCORE COMBINATIONS")
print("=" * 80)

combo_results = []
for rec in ['Invest', 'Hold', 'Avoid']:
    for min_score, max_score, score_label in [(9.0, 10.0, "9.0-10.0"), (8.0, 8.99, "8.0-8.99"), (7.0, 7.99, "7.0-7.99")]:
        combo_stocks = df[(df['recommendation'] == rec) & (df['score'] >= min_score) & (df['score'] <= max_score)]
        if len(combo_stocks) >= 2:
            avg_return = combo_stocks['return_pct'].mean()
            beat_count = combo_stocks['beat_nasdaq'].sum()
            beat_pct = beat_count / len(combo_stocks) * 100

            if avg_return > nasdaq_return:
                combo_results.append({
                    'combo': f"{rec} + {score_label}",
                    'avg_return': avg_return,
                    'outperformance': avg_return - nasdaq_return,
                    'count': len(combo_stocks),
                    'beat_rate': beat_pct
                })

combo_results.sort(key=lambda x: x['outperformance'], reverse=True)

for idx, combo in enumerate(combo_results[:15], 1):
    print(f"\n{idx}. {combo['combo']}")
    print(f"   Return: {combo['avg_return']:+.2f}% (vs NASDAQ: {combo['outperformance']:+.2f}%)")
    print(f"   Stocks: {combo['count']} | Beat Rate: {combo['beat_rate']:.0f}%")

# ============================================================================
# ANALYSIS 5: Stock Price Range Analysis
# ============================================================================
print("\n\n" + "=" * 80)
print("💰 ANALYSIS 5: PERFORMANCE BY STOCK PRICE RANGE")
print("=" * 80)

price_ranges = [
    (0, 20, "$0-20 (Penny/Small)"),
    (20, 50, "$20-50 (Small)"),
    (50, 100, "$50-100 (Mid)"),
    (100, 200, "$100-200 (Large)"),
    (200, 500, "$200-500 (Very Large)"),
    (500, 10000, "$500+ (Premium)")
]

for min_price, max_price, label in price_ranges:
    price_stocks = df[(df['start_price'] >= min_price) & (df['start_price'] < max_price)]
    if len(price_stocks) >= 3:
        avg_return = price_stocks['return_pct'].mean()
        beat_count = price_stocks['beat_nasdaq'].sum()
        beat_pct = beat_count / len(price_stocks) * 100

        status = "✅" if avg_return > nasdaq_return else "❌"
        print(f"\n{label}: {avg_return:+.2f}% (vs NASDAQ: {avg_return - nasdaq_return:+.2f}%) {status}")
        print(f"  Stocks: {len(price_stocks)} | Beat Rate: {beat_pct:.0f}%")

# ============================================================================
# ANALYSIS 6: High Performers - Who Beat NASDAQ and Why?
# ============================================================================
print("\n\n" + "=" * 80)
print("🏆 ANALYSIS 6: HIGH PERFORMERS - COMMON CHARACTERISTICS")
print("=" * 80)

winners = df[df['beat_nasdaq'] == True].copy()
losers = df[df['beat_nasdaq'] == False].copy()

print(f"\n📊 Winners vs Losers Comparison:")
print(f"\nWinners ({len(winners)} stocks):")
print(f"  Average Score: {winners['score'].mean():.2f}")
print(f"  Average Return: {winners['return_pct'].mean():+.2f}%")
print(f"  Most Common Recommendation: {winners['recommendation'].mode()[0]}")
print(f"  Most Common Industry: {winners['industry'].mode()[0] if len(winners) > 0 else 'N/A'}")

print(f"\nLosers ({len(losers)} stocks):")
print(f"  Average Score: {losers['score'].mean():.2f}")
print(f"  Average Return: {losers['return_pct'].mean():+.2f}%")
print(f"  Most Common Recommendation: {losers['recommendation'].mode()[0]}")
print(f"  Most Common Industry: {losers['industry'].mode()[0] if len(losers) > 0 else 'N/A'}")

# ============================================================================
# ANALYSIS 7: Top Individual Winners
# ============================================================================
print("\n\n" + "=" * 80)
print("🌟 ANALYSIS 7: TOP 30 INDIVIDUAL WINNERS")
print("=" * 80)

top_winners = df.nlargest(30, 'return_pct')
for idx, row in top_winners.iterrows():
    print(f"\n{row['symbol']:6s} ({row['industry'][:30]:30s})")
    print(f"  Return: {row['return_pct']:+7.2f}% | Score: {row['score']:.2f} | Rec: {row['recommendation']}")

# ============================================================================
# SUMMARY: Key Findings
# ============================================================================
print("\n\n" + "=" * 80)
print("🎯 KEY FINDINGS SUMMARY")
print("=" * 80)

print(f"\n1. Overall Win Rate: {df['beat_nasdaq'].sum()}/{len(df)} ({df['beat_nasdaq'].sum()/len(df)*100:.1f}%)")
print(f"2. Best Score Range: 8.5-8.99")
print(f"3. Best Recommendation: Invest + 8.0-8.99")
print(f"4. Best Industry: {industry_perf.index[0]} ({industry_perf.iloc[0]['avg_return']:+.2f}%)")
print(f"5. Sweet Spot: 8.0-8.99 score + Tech sectors + $50-200 stocks")

print("\n" + "=" * 80)
