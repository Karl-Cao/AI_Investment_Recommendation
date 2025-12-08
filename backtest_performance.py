import yfinance as yf
import pandas as pd
import json
import os
import sys
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Set UTF-8 encoding for output
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PortfolioBacktest:
    def __init__(self, start_date='2024-10-01', end_date=None):
        """
        Initialize the backtesting class

        Args:
            start_date: When the analysis was done (default: 2024-10-01)
            end_date: End date for comparison (default: today)
        """
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')

    def load_company_data(self):
        """Load the company analysis data"""
        consolidated_file = os.path.join("data", "consolidated_company_analysis.json")
        with open(consolidated_file, 'r') as f:
            data = json.load(f)

        # Load company symbols
        combined_file = os.path.join("data", "S&P500_related_tickers_combined.csv")
        combined_df = pd.read_csv(combined_file)

        return data, combined_df

    def get_stock_returns(self, symbol, start_date, end_date):
        """
        Calculate the return for a single stock

        Returns:
            dict: Contains return percentage and price data
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty or len(hist) < 2:
                return None

            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            return_pct = ((end_price - start_price) / start_price) * 100

            return {
                'symbol': symbol,
                'start_price': start_price,
                'end_price': end_price,
                'return_pct': return_pct,
                'history': hist
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_nasdaq_returns(self):
        """Get NASDAQ index returns for comparison"""
        return self.get_stock_returns('^IXIC', self.start_date, self.end_date)

    def calculate_portfolio_by_score(self, data, combined_df):
        """
        Calculate returns for portfolios grouped by ultimate strength score

        Returns:
            dict: Portfolio performance grouped by score ranges
        """
        # Define score ranges (inclusive on both ends)
        score_ranges = [
            (9.0, 10.0, "Excellent (9.0-10.0)"),
            (8.0, 8.99, "Very Good (8.0-8.99)"),
            (7.0, 7.99, "Good (7.0-7.99)"),
            (6.0, 6.99, "Above Average (6.0-6.99)"),
            (0, 5.99, "Average and Below (0-5.99)")
        ]

        portfolio_results = {}

        for min_score, max_score, label in score_ranges:
            companies_in_range = []

            # Find companies in this score range
            for company_name, details in data['company_analysis'].items():
                score = details.get('ultimate_strength', 0)
                recommendation = details.get('recommendation', '')

                if min_score <= score <= max_score:
                    # Get symbol for this company - try multiple matching strategies
                    company_row = combined_df[combined_df['name'].str.lower() == company_name.lower()]

                    # If exact match fails, try removing common suffixes and punctuation
                    if company_row.empty:
                        # Normalize: remove Inc, Corp, etc. and punctuation
                        normalized_name = company_name.lower().replace(',', '').replace('.', '').strip()
                        for suffix in [' inc', ' corp', ' corporation', ' incorporated', ' company', ' co', ' ltd']:
                            normalized_name = normalized_name.replace(suffix, '')
                        normalized_name = normalized_name.strip()

                        # Try fuzzy match
                        for idx, row in combined_df.iterrows():
                            csv_normalized = row['name'].lower().replace(',', '').replace('.', '').strip()
                            for suffix in [' inc', ' corp', ' corporation', ' incorporated', ' company', ' co', ' ltd']:
                                csv_normalized = csv_normalized.replace(suffix, '')
                            csv_normalized = csv_normalized.strip()

                            if normalized_name == csv_normalized:
                                company_row = combined_df.iloc[[idx]]
                                break

                    if not company_row.empty:
                        symbol = company_row.iloc[0]['symbol']
                        industry = company_row.iloc[0].get('industry', 'Unknown')
                        companies_in_range.append({
                            'name': company_name,
                            'symbol': symbol,
                            'score': score,
                            'recommendation': recommendation,
                            'industry': industry
                        })

            # Calculate returns for this portfolio
            if companies_in_range:
                returns = []
                successful_stocks = []

                for company in companies_in_range:
                    result = self.get_stock_returns(company['symbol'], self.start_date, self.end_date)
                    if result:
                        returns.append(result['return_pct'])
                        successful_stocks.append({
                            **company,
                            **result
                        })

                if returns:
                    portfolio_results[label] = {
                        'avg_return': sum(returns) / len(returns),
                        'best_return': max(returns),
                        'worst_return': min(returns),
                        'num_stocks': len(returns),
                        'total_companies': len(companies_in_range),
                        'stocks': successful_stocks
                    }

        return portfolio_results

    def calculate_recommendation_performance(self, data, combined_df):
        """
        Calculate returns grouped by recommendation (Invest/Hold/Avoid)
        """
        recommendations = ['Invest', 'Hold', 'Avoid']
        results = {}

        for rec in recommendations:
            companies = []

            # Find companies with this recommendation
            for company_name, details in data['company_analysis'].items():
                if details.get('recommendation', '') == rec:
                    company_row = combined_df[combined_df['name'].str.lower() == company_name.lower()]

                    # If exact match fails, try fuzzy matching
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
                        symbol = company_row.iloc[0]['symbol']
                        companies.append({
                            'name': company_name,
                            'symbol': symbol,
                            'score': details.get('ultimate_strength', 0),
                            'recommendation': rec
                        })

            # Calculate returns
            if companies:
                returns = []
                successful_stocks = []

                for company in companies:
                    result = self.get_stock_returns(company['symbol'], self.start_date, self.end_date)
                    if result:
                        returns.append(result['return_pct'])
                        successful_stocks.append({
                            **company,
                            **result
                        })

                if returns:
                    results[rec] = {
                        'avg_return': sum(returns) / len(returns),
                        'best_return': max(returns),
                        'worst_return': min(returns),
                        'num_stocks': len(returns),
                        'stocks': successful_stocks
                    }

        return results

    def calculate_sector_score_performance(self, data, combined_df):
        """
        Calculate returns grouped by sector AND score range
        This helps identify which sectors performed best within each score tier
        """
        # Collect all stocks with their sectors and scores
        all_stocks = []

        for company_name, details in data['company_analysis'].items():
            score = details.get('ultimate_strength', 0)
            company_row = combined_df[combined_df['name'].str.lower() == company_name.lower()]

            # If exact match fails, try fuzzy matching
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
                symbol = company_row.iloc[0]['symbol']
                industry = company_row.iloc[0].get('industry', 'Unknown')

                result = self.get_stock_returns(symbol, self.start_date, self.end_date)
                if result:
                    all_stocks.append({
                        'name': company_name,
                        'symbol': symbol,
                        'score': score,
                        'industry': industry,
                        'return_pct': result['return_pct'],
                        'start_price': result['start_price'],
                        'end_price': result['end_price']
                    })

        # Group by sector and score range
        sector_score_results = {}

        # Score ranges
        score_ranges = [
            (9.0, 10.0, "9.0-10.0"),
            (8.0, 8.99, "8.0-8.99"),
            (7.0, 7.99, "7.0-7.99"),
        ]

        for stock in all_stocks:
            industry = stock['industry']
            score = stock['score']

            # Find which score range this belongs to
            for min_score, max_score, score_label in score_ranges:
                if min_score <= score <= max_score:
                    key = f"{industry} ({score_label})"

                    if key not in sector_score_results:
                        sector_score_results[key] = {
                            'industry': industry,
                            'score_range': score_label,
                            'stocks': [],
                            'returns': []
                        }

                    sector_score_results[key]['stocks'].append(stock)
                    sector_score_results[key]['returns'].append(stock['return_pct'])
                    break

        # Calculate summary statistics for each sector+score combo
        for key, data in sector_score_results.items():
            returns = data['returns']
            if returns:
                data['avg_return'] = sum(returns) / len(returns)
                data['best_return'] = max(returns)
                data['worst_return'] = min(returns)
                data['num_stocks'] = len(returns)

        # Filter out groups with less than 2 stocks (not meaningful)
        sector_score_results = {k: v for k, v in sector_score_results.items() if v['num_stocks'] >= 2}

        return sector_score_results

    def generate_report(self):
        """Generate a comprehensive backtest report"""
        print("=" * 80)
        print(f"PORTFOLIO BACKTEST REPORT")
        print(f"Period: {self.start_date} to {self.end_date}")
        print("=" * 80)

        # Load data
        data, combined_df = self.load_company_data()

        # Get NASDAQ benchmark
        print("\n📊 BENCHMARK PERFORMANCE (NASDAQ)")
        print("-" * 80)
        nasdaq = self.get_nasdaq_returns()
        if nasdaq:
            print(f"NASDAQ Index (^IXIC)")
            print(f"  Starting Price: ${nasdaq['start_price']:,.2f}")
            print(f"  Ending Price:   ${nasdaq['end_price']:,.2f}")
            print(f"  Total Return:   {nasdaq['return_pct']:+.2f}%")
            nasdaq_return = nasdaq['return_pct']
        else:
            print("Failed to fetch NASDAQ data")
            nasdaq_return = 0

        # Performance by Score
        print("\n\n📈 PERFORMANCE BY ULTIMATE STRENGTH SCORE")
        print("-" * 80)
        score_results = self.calculate_portfolio_by_score(data, combined_df)

        for label, results in score_results.items():
            print(f"\n{label}")
            print(f"  Number of Stocks: {results['num_stocks']}/{results['total_companies']}")
            print(f"  Average Return:   {results['avg_return']:+.2f}%")
            print(f"  Best Return:      {results['best_return']:+.2f}%")
            print(f"  Worst Return:     {results['worst_return']:+.2f}%")
            print(f"  vs NASDAQ:        {results['avg_return'] - nasdaq_return:+.2f}%")

            # Show top performers
            sorted_stocks = sorted(results['stocks'], key=lambda x: x['return_pct'], reverse=True)
            print(f"\n  Top 5 Performers:")
            for stock in sorted_stocks[:5]:
                print(f"    {stock['symbol']:6s} ({stock['name'][:30]:30s}): {stock['return_pct']:+.2f}%")

        # Performance by Recommendation
        print("\n\n💡 PERFORMANCE BY RECOMMENDATION")
        print("-" * 80)
        rec_results = self.calculate_recommendation_performance(data, combined_df)

        for rec, results in rec_results.items():
            print(f"\n{rec}")
            print(f"  Number of Stocks: {results['num_stocks']}")
            print(f"  Average Return:   {results['avg_return']:+.2f}%")
            print(f"  Best Return:      {results['best_return']:+.2f}%")
            print(f"  Worst Return:     {results['worst_return']:+.2f}%")
            print(f"  vs NASDAQ:        {results['avg_return'] - nasdaq_return:+.2f}%")

        # Summary
        print("\n\n📊 SUMMARY")
        print("-" * 80)

        # Find best performing score range
        best_score_range = max(score_results.items(), key=lambda x: x[1]['avg_return'])
        print(f"Best Score Range: {best_score_range[0]} ({best_score_range[1]['avg_return']:+.2f}%)")

        # Find best recommendation
        if rec_results:
            best_rec = max(rec_results.items(), key=lambda x: x[1]['avg_return'])
            print(f"Best Recommendation: {best_rec[0]} ({best_rec[1]['avg_return']:+.2f}%)")

        print("\n" + "=" * 80)

        return {
            'nasdaq': nasdaq,
            'by_score': score_results,
            'by_recommendation': rec_results
        }

    def create_visualization(self, results):
        """Create visualizations of the backtest results"""

        # Create comparison chart
        fig = go.Figure()

        # Add NASDAQ benchmark
        nasdaq_return = results['nasdaq']['return_pct']

        # Add bars for score ranges
        score_labels = []
        score_returns = []

        for label, data in results['by_score'].items():
            score_labels.append(label)
            score_returns.append(data['avg_return'])

        fig.add_trace(go.Bar(
            name='Portfolio Returns by Score',
            x=score_labels,
            y=score_returns,
            marker_color='lightblue'
        ))

        # Add NASDAQ benchmark line
        fig.add_hline(y=nasdaq_return, line_dash="dash", line_color="red",
                     annotation_text=f"NASDAQ: {nasdaq_return:.2f}%",
                     annotation_position="right")

        fig.update_layout(
            title=f"Portfolio Performance vs NASDAQ ({self.start_date} to {self.end_date})",
            xaxis_title="Ultimate Strength Score Range",
            yaxis_title="Return (%)",
            showlegend=True,
            height=500
        )

        return fig


def main():
    # Create backtester
    backtester = PortfolioBacktest(start_date='2024-10-01')

    # Generate report
    results = backtester.generate_report()

    # Create visualization
    fig = backtester.create_visualization(results)
    fig.show()


if __name__ == "__main__":
    main()
