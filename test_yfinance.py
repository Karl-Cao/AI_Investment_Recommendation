import yfinance as yf
import pandas as pd
from datetime import datetime
import sys

# Set UTF-8 encoding for output
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_yfinance():
    """Test yfinance API functionality"""
    print("=" * 60)
    print("Testing yfinance API")
    print("=" * 60)

    # Test with a common stock (Apple)
    symbol = "AAPL"
    print(f"\n1. Testing with symbol: {symbol}")
    print("-" * 60)

    try:
        stock = yf.Ticker(symbol)
        print(f"[OK] Successfully created Ticker object for {symbol}")

        # Test 1: Get current info
        print("\n2. Testing current stock info...")
        try:
            info = stock.info
            if info:
                print(f"[OK] Got stock info")
                print(f"  - Company: {info.get('longName', 'N/A')}")
                print(f"  - Current Price: ${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}")
                print(f"  - Market Cap: {info.get('marketCap', 'N/A')}")
                print(f"  - Industry: {info.get('industry', 'N/A')}")
            else:
                print("[FAIL] No info data returned")
        except Exception as e:
            print(f"[FAIL] Error getting info: {str(e)}")

        # Test 2: Get historical data
        print("\n3. Testing historical data (6 months)...")
        try:
            hist = stock.history(period='6mo')
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                print(f"[OK] Got historical data")
                print(f"  - Data points: {len(hist)}")
                print(f"  - Date range: {hist.index.min().date()} to {hist.index.max().date()}")
                print(f"  - Latest close: ${hist['Close'].iloc[-1]:.2f}")
                print(f"  - Columns: {list(hist.columns)}")
                print(f"\n  Last 5 days:")
                print(hist[['Close', 'Volume']].tail())
            else:
                print("[FAIL] No historical data returned or empty DataFrame")
        except Exception as e:
            print(f"[FAIL] Error getting historical data: {str(e)}")

        # Test 3: Get earnings dates
        print("\n4. Testing earnings information...")
        try:
            # Try calendar first
            calendar = stock.calendar
            print(f"  Calendar type: {type(calendar)}")
            if calendar is not None:
                print(f"[OK] Got calendar data")
                print(f"  Calendar: {calendar}")
            else:
                print("  No calendar data available")
        except Exception as e:
            print(f"  Error getting calendar: {str(e)}")

        try:
            # Try earnings dates
            earnings_dates = stock.earnings_dates
            print(f"  Earnings dates type: {type(earnings_dates)}")
            if earnings_dates is not None:
                if isinstance(earnings_dates, pd.DataFrame) and not earnings_dates.empty:
                    print(f"[OK] Got earnings dates (DataFrame)")
                    print(f"  - Number of dates: {len(earnings_dates)}")
                    print(f"  - Latest dates:")
                    print(earnings_dates.head())
                else:
                    print(f"  Earnings dates: {earnings_dates}")
            else:
                print("  No earnings dates available")
        except Exception as e:
            print(f"  Error getting earnings dates: {str(e)}")

        # Test 4: Try another period
        print("\n5. Testing different historical periods...")
        for period in ['1mo', '3mo', '1y']:
            try:
                hist = stock.history(period=period)
                if isinstance(hist, pd.DataFrame) and not hist.empty:
                    print(f"[OK] {period}: {len(hist)} data points")
                else:
                    print(f"[FAIL] {period}: No data")
            except Exception as e:
                print(f"[FAIL] {period}: Error - {str(e)}")

    except Exception as e:
        print(f"[FAIL] Failed to create Ticker object: {str(e)}")

    # Test with another popular stock
    print("\n" + "=" * 60)
    print("6. Testing with additional symbols...")
    print("-" * 60)

    test_symbols = ["MSFT", "GOOGL", "TSLA"]
    for sym in test_symbols:
        try:
            stock = yf.Ticker(sym)
            hist = stock.history(period='1mo')
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                print(f"[OK] {sym}: Working - Latest close: ${hist['Close'].iloc[-1]:.2f}")
            else:
                print(f"[FAIL] {sym}: No data returned")
        except Exception as e:
            print(f"[FAIL] {sym}: Error - {str(e)}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_yfinance()
