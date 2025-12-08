"""
Quarterly Rebalancing Backtest
Compares quarterly rebalancing vs buy-and-hold vs NASDAQ
"""
from backtest_performance import PortfolioBacktest
import json
import os

class QuarterlyBacktest:
    def __init__(self):
        # Define quarters to test (we only have Oct 2024 data, so test monthly for now)
        self.test_periods = [
            ('2024-10-01', '2024-10-31', 'October 2024'),
            ('2024-11-01', '2024-11-30', 'November 2024'),
            ('2024-12-01', '2024-12-08', 'December 2024 (Current)')
        ]

    def run_monthly_rebalancing_simulation(self):
        """
        Simulate monthly rebalancing using current recommendations
        This is a proxy for quarterly rebalancing until we have multiple quarter data
        """
        print("=" * 80)
        print("MONTHLY REBALANCING SIMULATION")
        print("Strategy: Rebalance to winning sector-score combos each month")
        print("=" * 80)

        portfolio_value = 10000  # Start with $10,000
        monthly_returns = []

        for start_date, end_date, label in self.test_periods:
            print(f"\n{label}: {start_date} to {end_date}")

            backtester = PortfolioBacktest(start_date=start_date, end_date=end_date)
            data, combined_df = backtester.load_company_data()

            # Get sector-score performance for this period
            sector_results = backtester.calculate_sector_score_performance(data, combined_df)

            # Find top 3 winning sectors
            sorted_sectors = sorted(sector_results.items(),
                                   key=lambda x: x[1]['avg_return'],
                                   reverse=True)

            if len(sorted_sectors) >= 3:
                top_sectors = sorted_sectors[:3]
                avg_return = sum(s[1]['avg_return'] for s in top_sectors) / 3

                monthly_returns.append(avg_return)
                portfolio_value *= (1 + avg_return / 100)

                print(f"  Top 3 Sectors:")
                for i, (sector, result) in enumerate(top_sectors, 1):
                    print(f"    {i}. {sector[:50]:50s} {result['avg_return']:+7.2f}%")
                print(f"  Average Return: {avg_return:+.2f}%")
                print(f"  Portfolio Value: ${portfolio_value:,.2f}")

        print(f"\n{'=' * 80}")
        print(f"FINAL PORTFOLIO VALUE: ${portfolio_value:,.2f}")
        print(f"Total Return: {(portfolio_value - 10000) / 10000 * 100:+.2f}%")
        print(f"{'=' * 80}")

        return portfolio_value, monthly_returns

    def run_buyandhold_strategy(self):
        """
        Buy Oct 2024 recommendations and hold through Dec 2024
        """
        print("\n\n" + "=" * 80)
        print("BUY & HOLD STRATEGY")
        print("Strategy: Buy all 'Invest' recommendations in Oct, hold through Dec")
        print("=" * 80)

        backtester = PortfolioBacktest(start_date='2024-10-01', end_date='2024-12-08')
        data, combined_df = backtester.load_company_data()

        # Get all "Invest" recommendations
        score_results = backtester.calculate_portfolio_by_score(data, combined_df)

        if 'Excellent (9.0-10.0)' in score_results:
            excellent_return = score_results['Excellent (9.0-10.0)']['avg_return']
            portfolio_value = 10000 * (1 + excellent_return / 100)

            print(f"\nExcellent (9.0-10.0) Portfolio:")
            print(f"  Number of Stocks: {score_results['Excellent (9.0-10.0)']['num_stocks']}")
            print(f"  Average Return: {excellent_return:+.2f}%")
            print(f"  Final Value: ${portfolio_value:,.2f}")
            print(f"  Total Return: {(portfolio_value - 10000) / 10000 * 100:+.2f}%")

            return portfolio_value, excellent_return

        return 10000, 0

    def get_nasdaq_performance(self):
        """Get NASDAQ return for comparison period"""
        print("\n\n" + "=" * 80)
        print("NASDAQ BENCHMARK")
        print("=" * 80)

        backtester = PortfolioBacktest(start_date='2024-10-01', end_date='2024-12-08')
        nasdaq = backtester.get_nasdaq_returns()

        if nasdaq:
            nasdaq_return = nasdaq['return_pct']
            portfolio_value = 10000 * (1 + nasdaq_return / 100)

            print(f"\nNASDAQ Performance (Oct 1 - Dec 8, 2024):")
            print(f"  Return: {nasdaq_return:+.2f}%")
            print(f"  Final Value: ${portfolio_value:,.2f}")

            return portfolio_value, nasdaq_return

        return 10000, 0

    def run_sector_focused_strategy(self):
        """
        Strategy: Only invest in winning sector-score combinations
        """
        print("\n\n" + "=" * 80)
        print("SECTOR-FOCUSED STRATEGY (8.0-8.99 TECH)")
        print("Strategy: Only semiconductor/hardware companies rated 8.0-8.99")
        print("=" * 80)

        backtester = PortfolioBacktest(start_date='2024-10-01', end_date='2024-12-08')
        data, combined_df = backtester.load_company_data()

        sector_results = backtester.calculate_sector_score_performance(data, combined_df)

        # Focus on top tech sectors in 8.0-8.99 range
        tech_sectors = [
            'Semiconductor Equipment & Materials (8.0-8.99)',
            'Computer Hardware (8.0-8.99)',
            'Semiconductors (8.0-8.99)',
            'Electronic Components (8.0-8.99)'
        ]

        total_return = 0
        count = 0

        print("\nTech Sector Returns:")
        for sector in tech_sectors:
            if sector in sector_results:
                ret = sector_results[sector]['avg_return']
                total_return += ret
                count += 1
                print(f"  {sector[:55]:55s} {ret:+7.2f}%")

        if count > 0:
            avg_return = total_return / count
            portfolio_value = 10000 * (1 + avg_return / 100)

            print(f"\nAverage Tech Sector Return: {avg_return:+.2f}%")
            print(f"Final Value: ${portfolio_value:,.2f}")
            print(f"Total Return: {(portfolio_value - 10000) / 10000 * 100:+.2f}%")

            return portfolio_value, avg_return

        return 10000, 0

    def compare_all_strategies(self):
        """Compare all strategies and declare winner"""
        print("\n\n" + "=" * 80)
        print("STRATEGY COMPARISON - Oct 1 to Dec 8, 2024")
        print("=" * 80)

        # Run all strategies
        rebalance_value, rebalance_returns = self.run_monthly_rebalancing_simulation()
        buyhold_value, buyhold_return = self.run_buyandhold_strategy()
        nasdaq_value, nasdaq_return = self.get_nasdaq_performance()
        sector_value, sector_return = self.run_sector_focused_strategy()

        # Final comparison
        print("\n\n" + "=" * 80)
        print("FINAL RESULTS (Starting with $10,000)")
        print("=" * 80)

        strategies = [
            ("Monthly Rebalancing (Top 3 Sectors)", rebalance_value, (rebalance_value - 10000) / 100),
            ("Sector-Focused (8.0-8.99 Tech)", sector_value, (sector_value - 10000) / 100),
            ("Buy & Hold (Excellent 9.0-10.0)", buyhold_value, (buyhold_value - 10000) / 100),
            ("NASDAQ Benchmark", nasdaq_value, (nasdaq_value - 10000) / 100),
        ]

        strategies.sort(key=lambda x: x[1], reverse=True)

        for rank, (name, value, ret) in enumerate(strategies, 1):
            emoji = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"\n{rank}. {emoji} {name}")
            print(f"   Final Value: ${value:,.2f}")
            print(f"   Total Return: {ret:+.2f}%")
            if rank > 1:
                diff = value - strategies[0][1]
                print(f"   vs Winner: ${diff:,.2f} ({diff/strategies[0][1]*100:+.2f}%)")

        print("\n" + "=" * 80)
        print(f"🎯 WINNER: {strategies[0][0]}")
        print(f"   Outperformed NASDAQ by: {strategies[0][1] - nasdaq_value:,.2f}")
        print("=" * 80)

        # Key insights
        print("\n\n📊 KEY INSIGHTS:")
        print("-" * 80)

        if strategies[0][0].startswith("Sector-Focused"):
            print("✅ Sector-specific targeting (8.0-8.99 Tech) beats broad diversification")
            print("✅ Focus on Semiconductor Equipment, Hardware, and Components")
            print("✅ Score range 8.0-8.99 is the sweet spot, not 9.0-10.0")
        elif strategies[0][0].startswith("Monthly"):
            print("✅ Active rebalancing beats buy-and-hold")
            print("✅ Adapting to market changes improves performance")
        else:
            print("ℹ️  Strategy performance analysis needed")

        if buyhold_value < nasdaq_value:
            print("⚠️  Simple 'Excellent (9.0-10.0)' strategy underperforms NASDAQ")
            print("⚠️  Need sector-specific or score-adjusted approach")

        print("\n" + "=" * 80)

def main():
    backtest = QuarterlyBacktest()
    backtest.compare_all_strategies()

if __name__ == "__main__":
    main()
