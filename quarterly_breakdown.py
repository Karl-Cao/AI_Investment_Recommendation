"""
Quarterly Breakdown Analysis - Oct 2024 Recommendations Over 14 Months

This script analyzes how the October 2024 AI recommendations performed
quarter by quarter to show performance degradation over time.

Goal: Prove that quarterly rebalancing is necessary because recommendations
become stale and underperform as time passes.
"""
from backtest_performance import PortfolioBacktest
import pandas as pd
from datetime import datetime

class QuarterlyBreakdown:
    def __init__(self):
        # Define quarters from Oct 2024 to Dec 2025
        self.quarters = [
            ('2024-10-01', '2024-12-31', 'Q4 2024'),
            ('2025-01-01', '2025-03-31', 'Q1 2025'),
            ('2025-04-01', '2025-06-30', 'Q2 2025'),
            ('2025-07-01', '2025-09-30', 'Q3 2025'),
            ('2025-10-01', '2025-12-08', 'Q4 2025 (Current)')
        ]

        # Will store all winning strategies from Oct 2024 analysis
        self.oct_2024_data = None
        self.oct_2024_combined_df = None

    def load_october_2024_recommendations(self):
        """Load the original October 2024 AI analysis data"""
        print("=" * 80)
        print("LOADING OCTOBER 2024 AI RECOMMENDATIONS")
        print("=" * 80)

        # Use a dummy backtester just to load the data
        backtester = PortfolioBacktest(start_date='2024-10-01')
        data, combined_df = backtester.load_company_data()

        self.oct_2024_data = data
        self.oct_2024_combined_df = combined_df

        total_companies = len(data['company_analysis'])
        invest_count = sum(1 for c in data['company_analysis'].values() if c.get('recommendation') == 'Invest')

        print(f"\nTotal companies analyzed: {total_companies}")
        print(f"'Invest' recommendations: {invest_count}")
        print(f"Average score: {sum(c.get('ultimate_strength', 0) for c in data['company_analysis'].values()) / total_companies:.2f}")

    def test_quarter_performance(self, start_date, end_date, quarter_label):
        """Test how Oct 2024 recommendations performed in a specific quarter"""
        print(f"\n\n{'=' * 80}")
        print(f"QUARTER: {quarter_label} ({start_date} to {end_date})")
        print("=" * 80)

        backtester = PortfolioBacktest(start_date=start_date, end_date=end_date)

        # Get NASDAQ benchmark for this quarter
        nasdaq = backtester.get_nasdaq_returns()
        nasdaq_return = nasdaq['return_pct'] if nasdaq else 0

        print(f"\nNASDAQ Benchmark: {nasdaq_return:+.2f}%")

        # Test the winning strategies from Oct 2024
        print(f"\n{'─' * 80}")
        print("TESTING OCTOBER 2024 STRATEGIES IN THIS QUARTER")
        print('─' * 80)

        strategies = []

        # Strategy 1: All "Invest" recommendations (9.0-10.0)
        print("\n1. Traditional 'Invest' Portfolio (9.0-10.0)")
        score_results = backtester.calculate_portfolio_by_score(self.oct_2024_data, self.oct_2024_combined_df)

        if 'Excellent (9.0-10.0)' in score_results:
            excellent_return = score_results['Excellent (9.0-10.0)']['avg_return']
            num_stocks = score_results['Excellent (9.0-10.0)']['num_stocks']
            outperformance = excellent_return - nasdaq_return

            print(f"   Return: {excellent_return:+.2f}%")
            print(f"   vs NASDAQ: {outperformance:+.2f}%")
            print(f"   Stocks: {num_stocks}")

            status = "✅ BEAT" if excellent_return > nasdaq_return else "❌ LOST"
            print(f"   {status}")

            strategies.append({
                'name': 'Traditional Invest (9.0-10.0)',
                'return': excellent_return,
                'stocks': num_stocks,
                'beat_nasdaq': excellent_return > nasdaq_return
            })

        # Strategy 2: The "Sweet Spot" (8.0-8.99)
        print("\n2. Sweet Spot Portfolio (8.0-8.99)")
        if 'Very Good (8.0-8.99)' in score_results:
            very_good_return = score_results['Very Good (8.0-8.99)']['avg_return']
            num_stocks = score_results['Very Good (8.0-8.99)']['num_stocks']
            outperformance = very_good_return - nasdaq_return

            print(f"   Return: {very_good_return:+.2f}%")
            print(f"   vs NASDAQ: {outperformance:+.2f}%")
            print(f"   Stocks: {num_stocks}")

            status = "✅ BEAT" if very_good_return > nasdaq_return else "❌ LOST"
            print(f"   {status}")

            strategies.append({
                'name': 'Sweet Spot (8.0-8.99)',
                'return': very_good_return,
                'stocks': num_stocks,
                'beat_nasdaq': very_good_return > nasdaq_return
            })

        # Strategy 3: Top Sector Winners from Oct 2024 (Semiconductor Equipment 8.0-8.99)
        print("\n3. Top Oct 2024 Winner: Semiconductor Equipment (8.0-8.99)")
        sector_results = backtester.calculate_sector_score_performance(self.oct_2024_data, self.oct_2024_combined_df)

        semi_key = 'Semiconductor Equipment & Materials (8.0-8.99)'
        if semi_key in sector_results:
            semi_return = sector_results[semi_key]['avg_return']
            num_stocks = sector_results[semi_key]['num_stocks']
            outperformance = semi_return - nasdaq_return

            print(f"   Return: {semi_return:+.2f}%")
            print(f"   vs NASDAQ: {outperformance:+.2f}%")
            print(f"   Stocks: {num_stocks}")

            status = "✅ BEAT" if semi_return > nasdaq_return else "❌ LOST"
            print(f"   {status}")

            strategies.append({
                'name': 'Semiconductor Equipment (8.0-8.99)',
                'return': semi_return,
                'stocks': num_stocks,
                'beat_nasdaq': semi_return > nasdaq_return
            })

        # Strategy 4: Top 3 winning sectors from Oct 2024 (diversified)
        print("\n4. Top 3 Oct 2024 Sectors (Equal Weight)")

        # Get top sectors that beat NASDAQ in original analysis
        sorted_sectors = sorted(sector_results.items(),
                               key=lambda x: x[1]['avg_return'],
                               reverse=True)

        top_3_returns = []
        top_3_names = []
        for sector_name, sector_data in sorted_sectors[:3]:
            top_3_returns.append(sector_data['avg_return'])
            top_3_names.append(sector_name[:40])

        if len(top_3_returns) >= 3:
            avg_top3 = sum(top_3_returns) / 3
            outperformance = avg_top3 - nasdaq_return

            print(f"   Top 3: {', '.join(top_3_names[:2])}, ...")
            print(f"   Return: {avg_top3:+.2f}%")
            print(f"   vs NASDAQ: {outperformance:+.2f}%")

            status = "✅ BEAT" if avg_top3 > nasdaq_return else "❌ LOST"
            print(f"   {status}")

            strategies.append({
                'name': 'Top 3 Sectors (Diversified)',
                'return': avg_top3,
                'stocks': 'Multiple',
                'beat_nasdaq': avg_top3 > nasdaq_return
            })

        return {
            'quarter': quarter_label,
            'start_date': start_date,
            'end_date': end_date,
            'nasdaq_return': nasdaq_return,
            'strategies': strategies
        }

    def run_full_breakdown(self):
        """Run quarterly breakdown for all quarters"""
        print("=" * 80)
        print("QUARTERLY BREAKDOWN: OCT 2024 RECOMMENDATIONS OVER 14 MONTHS")
        print("Testing how recommendations perform as they get stale")
        print("=" * 80)

        # Load Oct 2024 data
        self.load_october_2024_recommendations()

        # Test each quarter
        all_quarter_results = []
        for start_date, end_date, quarter_label in self.quarters:
            quarter_result = self.test_quarter_performance(start_date, end_date, quarter_label)
            all_quarter_results.append(quarter_result)

        # Summary comparison
        print("\n\n" + "=" * 80)
        print("QUARTERLY PERFORMANCE SUMMARY")
        print("=" * 80)

        print("\n📊 How did each strategy perform quarter by quarter?\n")

        # Create a table view
        strategy_names = ['Traditional Invest (9.0-10.0)',
                         'Sweet Spot (8.0-8.99)',
                         'Semiconductor Equipment (8.0-8.99)',
                         'Top 3 Sectors (Diversified)']

        for strategy_name in strategy_names:
            print(f"\n{strategy_name}:")
            print(f"{'Quarter':<25} {'Return':<12} {'vs NASDAQ':<12} {'Result'}")
            print("-" * 65)

            for quarter_data in all_quarter_results:
                quarter_label = quarter_data['quarter']
                nasdaq_return = quarter_data['nasdaq_return']

                # Find this strategy in the quarter
                strategy = next((s for s in quarter_data['strategies'] if s['name'] == strategy_name), None)

                if strategy:
                    ret = strategy['return']
                    diff = ret - nasdaq_return
                    status = "✅ WIN" if strategy['beat_nasdaq'] else "❌ LOSE"

                    print(f"{quarter_label:<25} {ret:+7.2f}%     {diff:+7.2f}%     {status}")
                else:
                    print(f"{quarter_label:<25} {'N/A':<12} {'N/A':<12} -")

        # Win rate analysis
        print("\n\n" + "=" * 80)
        print("WIN RATE ANALYSIS")
        print("=" * 80)

        for strategy_name in strategy_names:
            wins = 0
            total = 0

            for quarter_data in all_quarter_results:
                strategy = next((s for s in quarter_data['strategies'] if s['name'] == strategy_name), None)
                if strategy:
                    total += 1
                    if strategy['beat_nasdaq']:
                        wins += 1

            win_rate = (wins / total * 100) if total > 0 else 0
            print(f"\n{strategy_name}")
            print(f"  Win Rate: {wins}/{total} quarters ({win_rate:.1f}%)")

            if win_rate < 50:
                print(f"  ⚠️  Loses to NASDAQ more than it wins")
            elif win_rate >= 80:
                print(f"  ✅ Strong consistent winner")
            else:
                print(f"  ⚖️  Mixed results")

        # Key insights
        print("\n\n" + "=" * 80)
        print("🎯 KEY INSIGHTS")
        print("=" * 80)

        # Calculate cumulative returns
        print("\n1. CUMULATIVE PERFORMANCE (Compound across all quarters):")
        print("   If you invested $10,000 in Oct 2024...\n")

        for strategy_name in strategy_names:
            portfolio_value = 10000

            for quarter_data in all_quarter_results:
                strategy = next((s for s in quarter_data['strategies'] if s['name'] == strategy_name), None)
                if strategy:
                    portfolio_value *= (1 + strategy['return'] / 100)

            total_return = (portfolio_value - 10000) / 10000 * 100
            print(f"   {strategy_name[:40]:40s} → ${portfolio_value:,.2f} ({total_return:+.2f}%)")

        # NASDAQ cumulative
        nasdaq_value = 10000
        for quarter_data in all_quarter_results:
            nasdaq_value *= (1 + quarter_data['nasdaq_return'] / 100)
        nasdaq_total = (nasdaq_value - 10000) / 10000 * 100

        print(f"   {'NASDAQ Benchmark':<40s} → ${nasdaq_value:,.2f} ({nasdaq_total:+.2f}%)")

        print("\n2. PERFORMANCE DEGRADATION:")
        print("   Did recommendations get worse over time?\n")

        # Compare early quarters vs late quarters
        for strategy_name in strategy_names:
            early_returns = []
            late_returns = []

            for i, quarter_data in enumerate(all_quarter_results):
                strategy = next((s for s in quarter_data['strategies'] if s['name'] == strategy_name), None)
                if strategy:
                    if i < 2:  # Q4 2024, Q1 2025
                        early_returns.append(strategy['return'])
                    else:  # Q2 2025, Q3 2025, Q4 2025
                        late_returns.append(strategy['return'])

            if early_returns and late_returns:
                avg_early = sum(early_returns) / len(early_returns)
                avg_late = sum(late_returns) / len(late_returns)
                degradation = avg_late - avg_early

                print(f"   {strategy_name[:40]:40s}")
                print(f"      Early (Q4 2024 - Q1 2025): {avg_early:+.2f}%")
                print(f"      Late  (Q2 2025 - Q4 2025): {avg_late:+.2f}%")

                if degradation < -5:
                    print(f"      ⚠️  Performance degraded by {abs(degradation):.1f}%")
                elif degradation > 5:
                    print(f"      ✅ Actually improved by {degradation:.1f}%")
                else:
                    print(f"      ⚖️  Stable ({degradation:+.1f}% change)")
                print()

        print("\n3. CONCLUSION:")

        # Check if any strategy consistently beats NASDAQ
        best_strategy = None
        best_win_rate = 0

        for strategy_name in strategy_names:
            wins = sum(1 for q in all_quarter_results
                      for s in q['strategies']
                      if s['name'] == strategy_name and s['beat_nasdaq'])
            total = sum(1 for q in all_quarter_results
                       for s in q['strategies']
                       if s['name'] == strategy_name)

            if total > 0:
                win_rate = wins / total * 100
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_strategy = strategy_name

        if best_win_rate < 60:
            print(f"\n   ❌ NO STRATEGY consistently beats NASDAQ (best: {best_win_rate:.0f}%)")
            print(f"   ⚠️  This confirms: 14-month hold is TOO LONG")
            print(f"   💡 SOLUTION: Quarterly rebalancing with fresh AI analysis")
        else:
            print(f"\n   ✅ {best_strategy} wins {best_win_rate:.0f}% of quarters")
            print(f"   💡 This strategy could work with quarterly updates")

        print("\n" + "=" * 80)

        return all_quarter_results


def main():
    breakdown = QuarterlyBreakdown()
    results = breakdown.run_full_breakdown()

    print("\n\n📋 NEXT STEPS:")
    print("-" * 80)
    print("1. Re-run AI analysis with current Dec 2025 data")
    print("2. Implement quarterly update pipeline")
    print("3. Update Streamlit to show quarterly performance tracking")
    print("4. Add 'staleness warning' when recommendations are > 3 months old")
    print("=" * 80)


if __name__ == "__main__":
    main()
