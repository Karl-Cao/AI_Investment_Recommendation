"""
Pattern-based analysis: Find patterns in winners
- Return magnitude patterns (small/medium/large gains)
- Consistency analysis (what % of stocks in each category win?)
- Risk/reward ratios
"""
from backtest_performance import PortfolioBacktest
import pandas as pd

# Create backtester
backtester = PortfolioBacktest(start_date='2024-12-01')

# Load data
data, combined_df = backtester.load_company_data()

# Get NASDAQ return
nasdaq = backtester.get_nasdaq_returns()
nasdaq_return = nasdaq['return_pct'] if nasdaq else 0

print("=" * 80)
print(f"PATTERN ANALYSIS - Finding Winning Formulas")
print(f"NASDAQ Benchmark: {nasdaq_return:+.2f}%")
print("=" * 80)

# Collect all stocks
all_stocks = []

for company_name, details in data['company_analysis'].items():
    score = details.get('ultimate_strength', 0)
    recommendation = details.get('recommendation', '')

    company_row = combined_df[combined_df['name'].str.lower() == company_name.lower()]

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
                'beat_nasdaq': result['return_pct'] > nasdaq_return,
                'outperformance': result['return_pct'] - nasdaq_return
            })

df = pd.DataFrame(all_stocks)

# ============================================================================
# PATTERN 1: Return Magnitude Categories
# ============================================================================
print("\n\n" + "=" * 80)
print("📊 PATTERN 1: RETURN MAGNITUDE CATEGORIES")
print("=" * 80)

magnitude_categories = [
    (100, 1000, "🚀 Explosive (100%+)"),
    (50, 100, "🔥 Very Strong (50-100%)"),
    (30, 50, "💪 Strong (30-50%)"),
    (nasdaq_return, 30, f"✅ Beat NASDAQ ({nasdaq_return:.0f}-30%)"),
    (0, nasdaq_return, f"⚠️  Positive but Lost to NASDAQ (0-{nasdaq_return:.0f}%)"),
    (-20, 0, "❌ Small Loss (0 to -20%)"),
    (-100, -20, "💀 Large Loss (-20% to -100%)")
]

for min_return, max_return, label in magnitude_categories:
    cat_stocks = df[(df['return_pct'] >= min_return) & (df['return_pct'] < max_return)]
    if len(cat_stocks) > 0:
        avg_score = cat_stocks['score'].mean()
        most_common_rec = cat_stocks['recommendation'].mode()[0] if len(cat_stocks) > 0 else 'N/A'
        most_common_industry = cat_stocks['industry'].mode()[0] if len(cat_stocks) > 0 else 'N/A'

        print(f"\n{label}")
        print(f"  Count: {len(cat_stocks)} stocks")
        print(f"  Avg Score: {avg_score:.2f}")
        print(f"  Most Common Rec: {most_common_rec}")
        print(f"  Top Industry: {most_common_industry[:40]}")

# ============================================================================
# PATTERN 2: Win Rate by Category
# ============================================================================
print("\n\n" + "=" * 80)
print("🎯 PATTERN 2: WIN RATE (% Beating NASDAQ) BY CATEGORY")
print("=" * 80)

# By Score
print("\n📈 By Score Range:")
score_ranges = [
    (9.0, 10.0, "9.0-10.0"),
    (8.0, 8.99, "8.0-8.99"),
    (7.0, 7.99, "7.0-7.99"),
    (6.0, 6.99, "6.0-6.99"),
    (5.0, 5.99, "5.0-5.99")
]

for min_score, max_score, label in score_ranges:
    score_stocks = df[(df['score'] >= min_score) & (df['score'] <= max_score)]
    if len(score_stocks) >= 3:
        win_count = score_stocks['beat_nasdaq'].sum()
        win_rate = win_count / len(score_stocks) * 100
        avg_return = score_stocks['return_pct'].mean()

        print(f"  {label}: {win_rate:.1f}% win rate ({win_count}/{len(score_stocks)}) | Avg: {avg_return:+.2f}%")

# By Recommendation
print("\n💡 By Recommendation:")
for rec in ['Invest', 'Hold', 'Avoid']:
    rec_stocks = df[df['recommendation'] == rec]
    if len(rec_stocks) > 0:
        win_count = rec_stocks['beat_nasdaq'].sum()
        win_rate = win_count / len(rec_stocks) * 100
        avg_return = rec_stocks['return_pct'].mean()

        print(f"  {rec}: {win_rate:.1f}% win rate ({win_count}/{len(rec_stocks)}) | Avg: {avg_return:+.2f}%")

# ============================================================================
# PATTERN 3: Best Combinations (Highest Win Rate)
# ============================================================================
print("\n\n" + "=" * 80)
print("🏆 PATTERN 3: HIGHEST WIN RATE COMBINATIONS (60%+ Win Rate)")
print("=" * 80)

high_win_rate_combos = []

# Industry + Score combinations
for industry in df['industry'].unique():
    for min_score, max_score, score_label in score_ranges:
        combo_stocks = df[(df['industry'] == industry) & (df['score'] >= min_score) & (df['score'] <= max_score)]
        if len(combo_stocks) >= 3:
            win_count = combo_stocks['beat_nasdaq'].sum()
            win_rate = win_count / len(combo_stocks) * 100
            avg_return = combo_stocks['return_pct'].mean()

            if win_rate >= 60:
                high_win_rate_combos.append({
                    'combo': f"{industry[:35]} ({score_label})",
                    'win_rate': win_rate,
                    'win_count': win_count,
                    'total': len(combo_stocks),
                    'avg_return': avg_return
                })

high_win_rate_combos.sort(key=lambda x: (x['win_rate'], x['avg_return']), reverse=True)

for idx, combo in enumerate(high_win_rate_combos[:20], 1):
    print(f"\n{idx}. {combo['combo']}")
    print(f"   Win Rate: {combo['win_rate']:.0f}% ({combo['win_count']}/{combo['total']})")
    print(f"   Avg Return: {combo['avg_return']:+.2f}%")

# ============================================================================
# PATTERN 4: Consistency Analysis
# ============================================================================
print("\n\n" + "=" * 80)
print("📉 PATTERN 4: CONSISTENCY - Which categories have NO big losers?")
print("=" * 80)

# Find combinations where NO stock lost more than 10%
print("\n🛡️  Safe Bets (No stock lost >10%):")

safe_combos = []
for industry in df['industry'].unique():
    for min_score, max_score, score_label in [(9.0, 10.0, "9.0-10.0"), (8.0, 8.99, "8.0-8.99"), (7.0, 7.99, "7.0-7.99")]:
        combo_stocks = df[(df['industry'] == industry) & (df['score'] >= min_score) & (df['score'] <= max_score)]
        if len(combo_stocks) >= 3:
            worst_loss = combo_stocks['return_pct'].min()
            if worst_loss > -10:
                avg_return = combo_stocks['return_pct'].mean()
                safe_combos.append({
                    'combo': f"{industry[:35]} ({score_label})",
                    'worst': worst_loss,
                    'avg': avg_return,
                    'count': len(combo_stocks)
                })

safe_combos.sort(key=lambda x: x['avg'], reverse=True)

for idx, combo in enumerate(safe_combos[:15], 1):
    print(f"\n{idx}. {combo['combo']}")
    print(f"   Avg Return: {combo['avg']:+.2f}% | Worst: {combo['worst']:+.2f}% | Stocks: {combo['count']}")

# ============================================================================
# PATTERN 5: The "Sure Thing" - 100% Win Rate
# ============================================================================
print("\n\n" + "=" * 80)
print("💎 PATTERN 5: THE 'SURE THINGS' - 100% Win Rate Combinations")
print("=" * 80)

sure_things = []
for industry in df['industry'].unique():
    for min_score, max_score, score_label in score_ranges:
        combo_stocks = df[(df['industry'] == industry) & (df['score'] >= min_score) & (df['score'] <= max_score)]
        if len(combo_stocks) >= 2:  # At least 2 stocks
            win_count = combo_stocks['beat_nasdaq'].sum()
            if win_count == len(combo_stocks):  # 100% win rate
                avg_return = combo_stocks['return_pct'].mean()
                sure_things.append({
                    'combo': f"{industry[:35]} ({score_label})",
                    'count': len(combo_stocks),
                    'avg_return': avg_return,
                    'best': combo_stocks['return_pct'].max(),
                    'worst': combo_stocks['return_pct'].min()
                })

sure_things.sort(key=lambda x: (x['count'], x['avg_return']), reverse=True)

for idx, combo in enumerate(sure_things[:20], 1):
    print(f"\n{idx}. {combo['combo']}")
    print(f"   Stocks: {combo['count']} (ALL beat NASDAQ)")
    print(f"   Avg: {combo['avg_return']:+.2f}% | Range: {combo['worst']:+.2f}% to {combo['best']:+.2f}%")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "=" * 80)
print("📋 ACTIONABLE INSIGHTS")
print("=" * 80)

print(f"\n1. 🎯 Best Win Rate: {high_win_rate_combos[0]['combo']} ({high_win_rate_combos[0]['win_rate']:.0f}%)")
print(f"2. 💎 Most Reliable: {len(sure_things)} combinations with 100% win rate")
print(f"3. 🛡️  Safest: {len(safe_combos)} combinations with no big losers")
print(f"4. 🚀 Explosive Gainers: {len(df[df['return_pct'] >= 100])} stocks gained 100%+")
print(f"5. 📊 Overall Win Rate: {df['beat_nasdaq'].sum()}/{len(df)} ({df['beat_nasdaq'].sum()/len(df)*100:.1f}%)")

print("\n" + "=" * 80)
