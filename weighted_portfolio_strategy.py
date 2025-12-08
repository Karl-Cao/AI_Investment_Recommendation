"""
Weighted Portfolio Strategy - Allocate based on Ultimate Strength Score
Higher scores get more capital allocation
"""
from backtest_performance import PortfolioBacktest
import pandas as pd

class WeightedPortfolioStrategy:
    def __init__(self, start_date='2024-12-01', end_date=None):
        self.backtester = PortfolioBacktest(start_date=start_date, end_date=end_date)
        self.start_date = start_date
        self.end_date = end_date

    def calculate_score_weights(self, stocks):
        """
        Calculate portfolio weights based on ultimate_strength scores
        Higher score = higher allocation

        Weight formula: weight = score^2 / sum(all scores^2)
        This gives exponential preference to higher scores
        """
        total_score_squared = sum(s['score'] ** 2 for s in stocks)

        for stock in stocks:
            stock['weight'] = (stock['score'] ** 2) / total_score_squared

        return stocks

    def run_weighted_strategy(self, sector_score_filter=None, min_score=8.0):
        """
        Run weighted portfolio strategy

        Args:
            sector_score_filter: List of sectors to focus on (e.g., tech sectors)
            min_score: Minimum score to include (default 8.0)
        """
        data, combined_df = self.backtester.load_company_data()

        # Collect all stocks that meet criteria
        eligible_stocks = []

        for company_name, details in data['company_analysis'].items():
            score = details.get('ultimate_strength', 0)

            # Filter by minimum score
            if score < min_score:
                continue

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
                symbol = self.backtester.clean_symbol(company_row.iloc[0]['symbol'])
                industry = company_row.iloc[0].get('industry', 'Unknown')

                # Apply sector filter if specified
                if sector_score_filter and industry not in sector_score_filter:
                    continue

                result = self.backtester.get_stock_returns(symbol, self.start_date, self.end_date)
                if result:
                    eligible_stocks.append({
                        'name': company_name,
                        'symbol': symbol,
                        'score': score,
                        'industry': industry,
                        'return_pct': result['return_pct']
                    })

        # Calculate weights based on scores
        weighted_stocks = self.calculate_score_weights(eligible_stocks)

        # Calculate weighted portfolio return
        weighted_return = sum(s['weight'] * s['return_pct'] for s in weighted_stocks)

        return weighted_return, weighted_stocks

    def run_all_weighted_strategies(self):
        """
        Test multiple weighted strategies and find the best one
        """
        print("=" * 80)
        print("WEIGHTED PORTFOLIO STRATEGIES")
        print(f"Period: {self.start_date} to {self.end_date or 'today'}")
        print("=" * 80)

        # Get NASDAQ benchmark
        nasdaq = self.backtester.get_nasdaq_returns()
        nasdaq_return = nasdaq['return_pct'] if nasdaq else 0
        print(f"\nNASDAQ Benchmark: {nasdaq_return:+.2f}%")

        strategies = []

        # Strategy 1: All stocks 8.0+, weighted by score
        print("\n\n" + "=" * 80)
        print("STRATEGY 1: All Stocks 8.0+ (Score-Weighted)")
        print("=" * 80)

        weighted_return, stocks = self.run_weighted_strategy(min_score=8.0)
        print(f"\nPortfolio Return: {weighted_return:+.2f}%")
        print(f"vs NASDAQ: {weighted_return - nasdaq_return:+.2f}%")
        print(f"Number of Stocks: {len(stocks)}")

        strategies.append({
            'name': 'All 8.0+ (Weighted)',
            'return': weighted_return,
            'stocks': len(stocks)
        })

        # Strategy 2: Tech sectors only, 8.0+
        print("\n\n" + "=" * 80)
        print("STRATEGY 2: Tech Sectors Only 8.0+ (Score-Weighted)")
        print("=" * 80)

        tech_sectors = [
            'Semiconductors',
            'Semiconductor Equipment & Materials',
            'Computer Hardware',
            'Electronic Components',
            'Software - Application',
            'Software - Infrastructure'
        ]

        weighted_return, stocks = self.run_weighted_strategy(
            sector_score_filter=tech_sectors,
            min_score=8.0
        )
        print(f"\nPortfolio Return: {weighted_return:+.2f}%")
        print(f"vs NASDAQ: {weighted_return - nasdaq_return:+.2f}%")
        print(f"Number of Stocks: {len(stocks)}")

        # Show top 10 holdings by weight
        stocks_sorted = sorted(stocks, key=lambda x: x['weight'], reverse=True)
        print(f"\nTop 10 Holdings (by weight):")
        for i, stock in enumerate(stocks_sorted[:10], 1):
            print(f"  {i:2d}. {stock['symbol']:6s} - Score: {stock['score']:.2f} - Weight: {stock['weight']*100:5.2f}% - Return: {stock['return_pct']:+7.2f}%")

        strategies.append({
            'name': 'Tech 8.0+ (Weighted)',
            'return': weighted_return,
            'stocks': len(stocks)
        })

        # Strategy 3: Top score range only (8.5-10.0)
        print("\n\n" + "=" * 80)
        print("STRATEGY 3: High Scores Only 8.5+ (Score-Weighted)")
        print("=" * 80)

        weighted_return, stocks = self.run_weighted_strategy(min_score=8.5)
        print(f"\nPortfolio Return: {weighted_return:+.2f}%")
        print(f"vs NASDAQ: {weighted_return - nasdaq_return:+.2f}%")
        print(f"Number of Stocks: {len(stocks)}")

        strategies.append({
            'name': 'High Score 8.5+ (Weighted)',
            'return': weighted_return,
            'stocks': len(stocks)
        })

        # Strategy 4: Semiconductor focus 8.0+
        print("\n\n" + "=" * 80)
        print("STRATEGY 4: Semiconductor Focus 8.0+ (Score-Weighted)")
        print("=" * 80)

        semi_sectors = [
            'Semiconductors',
            'Semiconductor Equipment & Materials'
        ]

        weighted_return, stocks = self.run_weighted_strategy(
            sector_score_filter=semi_sectors,
            min_score=8.0
        )
        print(f"\nPortfolio Return: {weighted_return:+.2f}%")
        print(f"vs NASDAQ: {weighted_return - nasdaq_return:+.2f}%")
        print(f"Number of Stocks: {len(stocks)}")

        strategies.append({
            'name': 'Semiconductor 8.0+ (Weighted)',
            'return': weighted_return,
            'stocks': len(stocks)
        })

        # Find winners
        print("\n\n" + "=" * 80)
        print("STRATEGY COMPARISON")
        print("=" * 80)

        strategies.sort(key=lambda x: x['return'], reverse=True)

        for rank, strategy in enumerate(strategies, 1):
            emoji = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            status = "✅ BEAT NASDAQ" if strategy['return'] > nasdaq_return else "❌ Lost to NASDAQ"

            print(f"\n{rank}. {emoji} {strategy['name']}")
            print(f"   Return: {strategy['return']:+.2f}%")
            print(f"   vs NASDAQ: {strategy['return'] - nasdaq_return:+.2f}%")
            print(f"   Stocks: {strategy['stocks']}")
            print(f"   {status}")

        print("\n" + "=" * 80)
        print(f"🎯 WINNER: {strategies[0]['name']}")
        print(f"   Outperformed NASDAQ by: {strategies[0]['return'] - nasdaq_return:+.2f}%")
        print("=" * 80)

        return strategies

def main():
    strategy = WeightedPortfolioStrategy(start_date='2024-12-01')
    results = strategy.run_all_weighted_strategies()

if __name__ == "__main__":
    main()
