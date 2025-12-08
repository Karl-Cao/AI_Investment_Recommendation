# 🤖 AI Investment Recommendation System

An intelligent investment analysis platform powered by Claude AI that provides stock recommendations, market insights, and portfolio backtesting capabilities.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.52+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 💬 AI Investment Assistant
- **Streaming Chat Interface** - Real-time responses powered by Claude 3.5 Sonnet
- **Context-Aware Analysis** - Maintains conversation history for personalized insights
- **Smart Company Detection** - Automatically detects stock symbols and provides quick links

### 📊 Comprehensive Analysis
- **Company Analysis** - Detailed insights on 270+ companies with Ultimate Strength scores
- **Sector Trends** - Industry-specific analysis and market trends
- **Real-time Stock Data** - Live price tracking and earnings information via Yahoo Finance
- **Interactive Visualizations** - Radar charts, price tracking, and performance graphs

### 🔬 Portfolio Backtesting
- **Performance Comparison** - Compare AI recommendations against NASDAQ index
- **Score-Based Analysis** - Group stocks by Ultimate Strength scores (9-10, 8-8.9, etc.)
- **Historical Returns** - Track performance from October 2024 to present
- **Interactive Charts** - Visual comparison with benchmark indices

### 🎯 Key Insights from Backtesting (Oct 2024 - Dec 2025)
- **Excellent Scores (9-10)**: +35.94% average return
- **Outperformed NASDAQ** by +4.30%
- **Top Performer**: CRDO +487.58%
- **NASDAQ Benchmark**: +31.65%

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Anthropic API key
- Git (for version control)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/AI_Investment_Recommendation.git
cd AI_Investment_Recommendation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your API key**

Create a `.streamlit/secrets.toml` file:
```toml
ANTHROPIC_API_KEY = "your-api-key-here"
```

**Important:** Never commit this file to GitHub! It's already in `.gitignore`.

4. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
AI_Investment_Recommendation/
├── app.py                          # Main Streamlit application
├── backtest_performance.py         # Backtesting logic
├── test_yfinance.py               # Yahoo Finance API testing
├── data/
│   ├── consolidated_company_analysis.json
│   ├── S&P500_related_tickers_combined.csv
│   └── S&P500_standardized.csv
├── .streamlit/
│   └── secrets.toml               # API keys (not in git)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── README_BACKTEST.md            # Backtest feature documentation
└── .gitignore                    # Git ignore rules
```

## 🎮 Usage

### Chat with AI Assistant
1. Navigate to the **💬 AI Investment Assistant** tab
2. Ask questions like:
   - "What are the top performing tech companies?"
   - "Compare Apple and Microsoft's performance"
   - "Which sectors show the most promise?"

### View Company Analysis
1. Go to **🏢 Company Analysis**
2. Search for a company by name or symbol
3. View detailed metrics, earnings info, and price charts

### Run Backtest Analysis
1. Click **🔬 Backtest Performance**
2. Select your analysis start date
3. View performance by score ranges vs NASDAQ

## 📊 Data Sources

- **Company Analysis**: AI-generated recommendations with Ultimate Strength scores
- **Stock Prices**: Yahoo Finance API via yfinance
- **Market Data**: S&P 500 and related tickers
- **Benchmark**: NASDAQ Composite (^IXIC)

## 🔑 Environment Variables

Create a `.streamlit/secrets.toml` file with:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."  # Your Anthropic API key
```

**For Streamlit Cloud deployment**, add this in the Streamlit dashboard under "Secrets".

## 🛠️ Technologies Used

- **Frontend**: Streamlit
- **AI Model**: Claude 3.5 Sonnet (Anthropic)
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Plotly
- **Stock Data**: yfinance
- **Language**: Python 3.13

## 📈 Key Metrics

The AI analysis includes:
- **Ultimate Strength Score** (0-10) - Overall company strength
- **Recommendation** - Invest/Hold/Avoid
- **Industry Analysis** - Sector-specific insights
- **Market Cap** - Company valuation
- **Earnings Data** - Next/last earnings dates

## 🧪 Testing

Test the Yahoo Finance API connection:
```bash
python test_yfinance.py
```

Run backtest analysis from command line:
```bash
python backtest_performance.py
```

## 📝 Requirements

```txt
yfinance>=0.2.66
pandas>=2.3.3
plotly>=6.5.0
streamlit>=1.52.1
anthropic>=0.75.0
```

## 🚀 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your `ANTHROPIC_API_KEY` in Secrets
5. Deploy!

### Local Deployment

```bash
streamlit run app.py --server.port 8501
```

## 🔒 Security

- ✅ API keys stored in `.streamlit/secrets.toml` (gitignored)
- ✅ No hardcoded credentials
- ✅ Secure environment variable handling
- ⚠️ Never commit `secrets.toml` to GitHub

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Some stocks may be delisted and won't have price data
- Earnings dates require `lxml` library (optional)
- First backtest run may take 1-2 minutes (subsequent runs are cached)

## 🔮 Future Enhancements

- [ ] S&P 500 comparison alongside NASDAQ
- [ ] Risk-adjusted returns (Sharpe ratio)
- [ ] Sector-specific backtests
- [ ] Monthly rebalancing simulation
- [ ] Portfolio optimization tools
- [ ] Export reports to PDF

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the [Backtest Documentation](README_BACKTEST.md)

## 🙏 Acknowledgments

- **Anthropic** - Claude AI API
- **Yahoo Finance** - Stock market data
- **Streamlit** - Web framework
- **Plotly** - Data visualization

---

**⭐ If you find this project helpful, please give it a star!**

Made with ❤️ and 🤖 AI
