import os
import json
import re
import pandas as pd
from anthropic import Anthropic
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Initialize Anthropic client
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

class InvestmentChatbot:
    def __init__(self):
        self.system_prompt = """You are an investment analysis assistant. You have access to detailed company analysis data including:
        - Company recommendations (Invest/Hold/Avoid)
        - Ultimate strength scores
        - Industry-specific analysis
        - Market trends
        - Company-specific metrics and explanations
        
        Use this data to provide informed responses about investment opportunities and market trends.
        Always explain your reasoning and cite specific metrics when making recommendations.
        Remember previous context in the conversation to provide more relevant and personalized responses.
        """
        
    def prepare_context(self, data, query):
        """Prepare relevant context based on the user's query"""
        context = []
        
        # Add relevant company data
        for company, details in data['company_analysis'].items():
            if company.lower() in query.lower():
                context.append(f"Company Analysis for {company}:")
                context.append(f"Recommendation: {details['recommendation']}")
                context.append(f"Ultimate Strength: {details['ultimate_strength']}")
                context.append(f"Industry: {details.get('industry', 'N/A')}")
                context.append(f"Explanation: {details.get('explanation', '')}")
                
        # Add sector trends if mentioned
        for sector, analysis in data['consolidated_trends'].items():
            if sector.lower() in query.lower():
                context.append(f"\nSector Analysis for {sector}:")
                context.append(analysis)
                
        return "\n".join(context)

    def get_response(self, query, data):
        context = self.prepare_context(data, query)
        
        # Include previous conversation context
        messages = []
        if 'messages' in st.session_state:
            # Get last 5 messages for context (adjust number as needed)
            recent_messages = st.session_state.messages[-5:]
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        try:
            response = anthropic.messages.create(
                model="claude-3-5-sonnet-latest",
                system=f"{self.system_prompt}\n\nRelevant Data:\n{context}",
                max_tokens=1024,
                messages=messages
            )
            
            # Handle the response properly
            return self.extract_response_content(response)
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")
            return "I apologize, but I encountered an error. Could you please rephrase your question?"

    def extract_response_content(self, response):
        """Extract the text content from the response object"""
        # If response is a list
        if isinstance(response, list):
            response_parts = []
            for item in response:
                # Assuming the response is in the format: TextBlock(text="...", type='text')
                match = re.search(r'text="(.*?)"', item, re.DOTALL)
                if match:
                    response_parts.append(match.group(1))

            # Join all parts to form the full response
            return ' '.join(response_parts)

        # If response is a single object with a content attribute
        elif hasattr(response, 'content'):
            return response.content

        # If response is already a string, return it
        elif isinstance(response, str):
            return response

        # Fallback in case of an unexpected format
        return str(response)


def add_chatbot_interface(data):
    st.title("Investment Analysis Chatbot")
    
    # Initialize session state for chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize chatbot
    chatbot = InvestmentChatbot()
    
    # Create a mapping of symbols to company names from your data
    symbol_to_company = {}
    for company_name, details in data['company_analysis'].items():
        if 'symbols' in details:
            for symbol in details['symbols'].split(','):
                symbol_to_company[symbol.strip()] = company_name
    
    # Function to create company links and buttons
    def add_company_links(text):
        import re
        # Pattern to match stock symbols in parentheses: (XXXX)
        pattern = r'\(([A-Z]{1,5})\)'
        
        def replace_with_links(match):
            symbol = match.group(1)
            company_name = symbol_to_company.get(symbol)
            
            # Create columns for the buttons
            col1, col2 = st.columns(2)
            
            # Internal company analysis link
            if company_name:
                with col1:
                    if st.button(f"📊 View {company_name} Analysis", key=f"company_{symbol}"):
                        navigate_to_company(company_name)
            
            # External Yahoo Finance link
            with col2:
                if st.button(f"🔗 Yahoo Finance ({symbol})", key=f"yahoo_{symbol}"):
                    st.write(f"[🔗 Yahoo Finance ({symbol})](https://finance.yahoo.com/quote/{symbol})")

            
            return f"**{symbol}**"  # Keep the symbol visible in the text
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # First display the text with bold symbols
                content = message["content"]
                if isinstance(content, list):
                    content = ' '.join(str(item) for item in content)
                
                # Add links and buttons for stock symbols
                linked_content = re.sub(r'\(([A-Z]{1,5})\)', r'**(\1)**', content)
                st.markdown(linked_content)
                
                # Then add the buttons for each symbol
                symbols = re.findall(r'\(([A-Z]{1,5})\)', content)
                if symbols:
                    st.write("Quick Links:")
                    for symbol in symbols:
                        company_name = symbol_to_company.get(symbol)
                        col1, col2 = st.columns(2)
                        
                        if company_name:
                            with col1:
                                if st.button(f"📊 View {company_name} Analysis", key=f"hist_company_{symbol}_{len(st.session_state.messages)}"):
                                    navigate_to_company(company_name)
                        
                        with col2:
                            if st.button(f"🔗 Yahoo Finance ({symbol})", key=f"hist_yahoo_{symbol}_{len(st.session_state.messages)}"):
                                st.markdown(f"<script>window.open('https://finance.yahoo.com/quote/{symbol}', '_blank');</script>", unsafe_allow_html=True)
                        
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about investment opportunities..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            response = chatbot.get_response(prompt, data)
            
            # Handle response formatting
            if isinstance(response, list):
                response_parts = []
                for item in response:
                    if hasattr(item, 'text'):
                        response_parts.append(item.text)
                    elif isinstance(item, dict) and 'text' in item:
                        response_parts.append(item['text'])
                    else:
                        response_parts.append(str(item))
                response = ' '.join(response_parts)
            elif hasattr(response, 'text'):
                response = response.text
            elif isinstance(response, dict) and 'text' in response:
                response = response['text']
            
            # Display formatted response with links
            linked_response = re.sub(r'\(([A-Z]{1,5})\)', r'**(\1)**', response)
            st.markdown(linked_response)
            
            # Extract symbols from the response
            symbols = re.findall(r'\(([A-Z]{1,5})\)', response)

            # Extract company names from the response
            company_names = []
            for company in symbol_to_company.values():
                if company.lower() in response.lower():
                    company_names.append(company)

            # Use a set to avoid duplicates in case both the symbol and the company name are found
            unique_matches = set(symbols + company_names)

            if unique_matches:
                st.write("Quick Links:")

                # Iterate over unique matches
                for match in unique_matches:
                    # Determine if the match is a symbol or a company name
                    if match in symbol_to_company:
                        # It's a stock symbol, get the corresponding company name
                        company_name = symbol_to_company[match]
                        symbol = match
                    else:
                        # It's a company name, get the corresponding symbol
                        company_name = match
                        # Reverse lookup for the symbol from the company name
                        symbol = next((key for key, value in symbol_to_company.items() if value == company_name), None)

                    # Ensure we have both company_name and symbol before generating buttons
                    if company_name and symbol:
                        # Create buttons for both company analysis and Yahoo Finance
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button(f"📊 View {company_name} Analysis", key=f"resp_company_{symbol}"):
                                navigate_to_company(company_name)

                        with col2:
                            yahoo_link = f"https://finance.yahoo.com/quote/{symbol}"
                            st.markdown(f"[🔗 Yahoo Finance ({symbol})]({yahoo_link})", unsafe_allow_html=True)


            
            # Add a divider for clarity
            st.divider()
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Load data
@st.cache_data
def load_data():
    # Load consolidated analysis JSON
    consolidated_file = os.path.join("data", "consolidated_company_analysis.json")
    with open(consolidated_file, 'r') as f:
        data = json.load(f)

    # Load additional company details from CSV
    combined_file = os.path.join("data", "S&P500_related_tickers_combined.csv")
    combined_df = pd.read_csv(combined_file)

    # Normalize company names for consistent matching
    combined_df['normalized_name'] = combined_df['name'].apply(normalize_company_name)

    # Enrich each company in the JSON with details from the CSV
    for company_name, company_data in data['company_analysis'].items():
        normalized_name = normalize_company_name(company_name)

        # Find the row in the CSV that matches the company
        matching_row = combined_df[combined_df['normalized_name'] == normalized_name]
        if not matching_row.empty:
            row = matching_row.iloc[0]
            company_data['industry'] = row.get('industry', 'N/A')
            company_data['market_cap'] = row.get('market_cap', 'N/A')
            company_data['country'] = row.get('country', 'N/A')
            company_data['website'] = row.get('website', 'N/A')
            company_data['symbols'] = row.get('symbol', 'N/A')

    return data

@st.cache_data
def load_sp500_data():
    # Load S&P 500 data
    sp500_file = os.path.join("data", "S&P500_standardized.csv")
    sp500_df = pd.read_csv(sp500_file)
    return sp500_df

def normalize_company_name(name):
    """Normalize company name for consistent matching."""
    if pd.isna(name):
        return ""
    name = name.replace('.', '').replace(',', '').strip().lower()
    return name

def format_market_cap(value):
    """Format market cap to human readable format with B/M suffix"""
    try:
        value = float(value)
        if value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def navigate_to_company(company_name):
    st.session_state.selected_company = company_name
    st.session_state.active_tab = "Company Analysis"
    st.rerun()

def navigate_to_sector(sector_name):
    st.session_state.selected_sector = sector_name
    st.session_state.active_tab = "Sector Trends"
    st.rerun()

def show_overview(data):
    st.header("Investment Analysis Overview")

    # Create a DataFrame from the company analysis data
    df = pd.DataFrame.from_dict(data['company_analysis'], orient='index')
    df['company'] = df.index
    df['recommendation'] = df['recommendation'].astype('category')

    # Display some key statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Companies Analyzed", len(df))
    col2.metric("Companies Recommended for Investment", len(df[df['recommendation'] == 'Invest']))
    col3.metric("Average Ultimate Strength", f"{df['ultimate_strength'].mean():.2f}")

    # Plot distribution of ultimate strength
    fig = px.histogram(df, x='ultimate_strength', nbins=20, title="Distribution of Ultimate Strength Scores")
    st.plotly_chart(fig)

    # Display companies grouped by score with clickable links
    st.subheader("Companies Grouped by Ultimate Strength Score")
    unique_scores = df['ultimate_strength'].unique()
    unique_scores.sort()

    score_selection = st.multiselect("Select scores to view companies", unique_scores[::-1])
    
    if score_selection:
        companies_with_selected_scores = df[df['ultimate_strength'].isin(score_selection)][['company', 'ultimate_strength', 'recommendation']]
        companies_with_selected_scores = companies_with_selected_scores.sort_values(by='ultimate_strength', ascending=False)
        
        # Create clickable company names
        for _, row in companies_with_selected_scores.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button(f"📊 {row['company']}", key=f"btn_{row['company']}"):
                    navigate_to_company(row['company'])
            with col2:
                st.write(f"Score: {row['ultimate_strength']:.2f}")
            with col3:
                st.write(f"Recommendation: {row['recommendation']}")

def show_company_analysis(data, sp500_companies):
    st.header("Company Analysis")

    companies = list(data['company_analysis'].keys())

    # Add search and filter options
    search_term = st.text_input("Search for a company or symbol", 
                               st.session_state.selected_company if st.session_state.selected_company else "").lower()
    filter_sp500 = st.checkbox("Show only S&P 500 companies")
    filter_non_sp500 = st.checkbox("Show only companies not in the S&P 500")

    # Filter companies based on checkboxes
    filtered_companies = [
        company for company in companies
        if ((not filter_sp500 or normalize_company_name(company) in sp500_companies) and
            (not filter_non_sp500 or normalize_company_name(company) not in sp500_companies)) and
            (search_term in company.lower() or 
             (data['company_analysis'][company].get('symbols', '') and 
              any(search_term in symbol.lower() for symbol in data['company_analysis'][company]['symbols'].split(','))))
    ]

    if filtered_companies:
        selected_idx = 0
        if st.session_state.selected_company in filtered_companies:
            selected_idx = filtered_companies.index(st.session_state.selected_company)
            
        selected_company = st.selectbox("Select a company from the list", 
                                      filtered_companies,
                                      index=selected_idx)
        
        company_data = data['company_analysis'][selected_company]
        display_company_info(company_data, selected_company, data)
    else:
        st.warning("No companies found matching your search term.")

def display_company_info(company_data, company_name, full_data):
    st.subheader(f"{company_name} Analysis")

    # Get earnings info using yfinance
    symbol = company_data.get('symbols', '').split(',')[0].strip()
    earnings_info = {'next': None, 'last': None}

    if symbol:
        try:
            stock = yf.Ticker(symbol)
            
            # Get earnings information using proper type checking
            try:
                # First try to get calendar info for next earnings
                calendar = stock.calendar
                if calendar is not None:
                    if isinstance(calendar, dict):
                        # Handle dictionary format
                        if 'Earnings Date' in calendar:
                            next_earnings = calendar['Earnings Date']
                            if isinstance(next_earnings, (list, tuple)) and len(next_earnings) > 0:
                                earnings_info['next'] = pd.Timestamp(next_earnings[0]).strftime('%Y-%m-%d')
                    else:
                        # Handle DataFrame format
                        try:
                            next_earnings = calendar.loc['Earnings Date', 0]
                            if pd.notna(next_earnings):
                                earnings_info['next'] = pd.Timestamp(next_earnings).strftime('%Y-%m-%d')
                        except:
                            pass

                # Get historical earnings dates
                earnings_dates = stock.earnings_dates
                if earnings_dates is not None:
                    if isinstance(earnings_dates, pd.DataFrame) and not earnings_dates.empty:
                        today = pd.Timestamp.now()
                        past_dates = earnings_dates[earnings_dates.index < today]
                        if not past_dates.empty:
                            last_earnings_date = past_dates.index.max()
                            earnings_info['last'] = pd.Timestamp(last_earnings_date).strftime('%Y-%m-%d')
                    elif isinstance(earnings_dates, dict):
                        # Handle dictionary format
                        dates = sorted([pd.Timestamp(date) for date in earnings_dates.keys()])
                        if dates:
                            earnings_info['last'] = dates[-1].strftime('%Y-%m-%d')

                # If we still don't have last earnings, try quarterly earnings
                if not earnings_info['last']:
                    quarterly = stock.quarterly_earnings
                    if quarterly is not None:
                        if isinstance(quarterly, pd.DataFrame) and not quarterly.empty:
                            last_date = quarterly.index.max()
                            earnings_info['last'] = pd.Timestamp(last_date).strftime('%Y-%m-%d')
                        elif isinstance(quarterly, dict) and quarterly:
                            dates = sorted([pd.Timestamp(date) for date in quarterly.keys()])
                            if dates:
                                earnings_info['last'] = dates[-1].strftime('%Y-%m-%d')
                        
            except Exception as e:
                print(f"Error fetching earnings data for {symbol}: {str(e)}")

        except Exception as e:
            print(f"Error accessing data for {symbol}: {str(e)}")

    # Display earnings information
    st.write("---")
    st.write("**📅 Earnings Information**")

    col1, col2 = st.columns(2)
    
    with col1:
        # Display next earnings date(s)
        if earnings_info.get('next'):
            st.write(f"**Next Earnings:** {earnings_info['next']}")
        else:
            st.write("**Next Earnings:** Date not announced")

    with col2:
        # Display last earnings date
        if earnings_info.get('last'):
            st.write(f"**Last Reported:** {earnings_info['last']}")
        else:
            st.write("**Last Reported:** No data available")

    # Rest of your display code remains the same...
    # Company details
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Recommendation:** {company_data.get('recommendation', 'N/A')}")
        st.write(f"**Ultimate Strength:** {company_data.get('ultimate_strength', 'N/A')}")
        st.write(f"**Industry:** {company_data.get('industry', 'N/A')}")

        if company_data.get('industry') != 'N/A':
            if st.button(f"📈 View {company_data['industry']} Sector Trends", key=f"view_sector_{company_data['industry']}"):
                navigate_to_sector(company_data['industry'])

    with col2:
        st.write(f"**Market Cap:** {format_market_cap(company_data.get('market_cap', 'N/A'))}")
        st.write(f"**Country:** {company_data.get('country', 'N/A')}")
        website = company_data.get('website', 'N/A')
        if website != 'N/A':
            st.write(f"**Website:** [Link]({website})")
        else:
            st.write(f"**Website:** {website}")

    # Radar chart for scores (if available)
    if 'scores' in company_data:
        categories = list(company_data['scores'].keys())
        values = list(company_data['scores'].values())

        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=False
        )

        st.plotly_chart(fig)

    # Explanation
    st.subheader("Analysis Explanation")
    st.write(company_data.get('explanation', 'N/A'))

    # Stock Price Tracking
    st.subheader("Stock Price Tracking")
    if symbol:
        try:
            price_data = stock.history(period='6mo')
            if isinstance(price_data, pd.DataFrame) and not price_data.empty:
                st.line_chart(price_data['Close'])
            else:
                st.warning("No price data available for this period")
        except Exception as e:
            print(f"Error fetching price data: {str(e)}")

def show_sector_trends(data):
    st.header("Market Trends")

    # Get list of sectors
    sectors = list(data['consolidated_trends'].keys())

    # Use session state for sector selection if available
    selected_idx = 0
    if st.session_state.selected_sector in sectors:
        selected_idx = sectors.index(st.session_state.selected_sector)
        
    selected_sector = st.selectbox("Select a sector to view analysis", 
                                 sectors,
                                 index=selected_idx)

    if selected_sector:
        st.subheader(f"{selected_sector.capitalize()} Sector Analysis")
        st.write(data['consolidated_trends'][selected_sector])

        # Show companies in this sector with links to their analysis
        st.subheader(f"Companies in {selected_sector}")
        sector_companies = [
            company for company, details in data['company_analysis'].items()
            if details.get('industry') == selected_sector
        ]
        
        for company in sector_companies:
            if st.button(f"📊 View {company} Analysis", key=f"sector_company_{company}"):
                navigate_to_company(company)

def suggest_company():
    st.header("Suggest a Company for Analysis")
    suggested_company = st.text_input("Enter the name or symbol of a company that you think should be analyzed")

    if suggested_company:
        st.write(f"Thanks! We'll consider adding '{suggested_company}' to the analysis in the future.")

def main():
    st.set_page_config(layout="wide", page_title="Investment Analysis AI Assistant")
    
    # Initialize session states
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'selected_sector' not in st.session_state:
        st.session_state.selected_sector = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Chat"  # Set Chat as default
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    # Load data
    data = load_data()
    sp500_df = load_sp500_data()
    sp500_companies = set(sp500_df['name'].apply(normalize_company_name))

    # Sidebar navigation
    st.sidebar.title("Navigation")
    nav_options = {
        "Chat": "💬 AI Investment Assistant",
        "Overview": "📊 Market Overview",
        "Company Analysis": "🏢 Company Analysis",
        "Sector Trends": "📈 Sector Trends",
        "Suggest a Company": "💡 Suggest a Company"
    }
    
    for key, label in nav_options.items():
        if st.sidebar.button(label, key=f"nav_{key}"):
            st.session_state.active_tab = key

    # Add sidebar info about the assistant
    with st.sidebar.expander("ℹ️ About this AI Assistant"):
        st.write("""
        This AI Investment Assistant helps you:
        - Analyze companies and their financials
        - Compare investment opportunities
        - Track market trends and sectors
        - Get real-time stock insights
        
        Simply ask questions in natural language!
        """)

    # Render content based on active tab
    if st.session_state.active_tab == "Chat":
        # Welcome message for first-time visitors
        if st.session_state.first_visit:
            st.snow()  # Add a fun welcome effect
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.success("""
                👋 Welcome to your AI Investment Assistant!
                
                I can help you with:
                - Company analysis and recommendations
                - Market trends and insights
                - Investment strategies
                - Stock comparisons
                
                Try asking me questions like:
                - "What are some promising tech companies to invest in?"
                - "Compare Apple and Microsoft's performance"
                - "What are the trends in the healthcare sector?"
                
                Just type your question below to get started!
                """)
            st.session_state.first_visit = False
            
        add_chatbot_interface(data)
        
        # Add helpful examples at the bottom
        with st.expander("🎯 Example Questions"):
            st.write("""
            Here are some questions you can ask:
            
            **Company Analysis**
            - "What are the top performing companies in the tech sector?"
            - "Tell me about companies with strong growth potential"
            - "Which companies have the highest ultimate strength scores?"
            
            **Market Research**
            - "What are the current trends in renewable energy?"
            - "How is the banking sector performing?"
            - "Which sectors show the most promise for 2024?"
            
            **Investment Strategy**
            - "What are some low-risk investment options?"
            - "Show me companies with strong dividends"
            - "Compare the performance of major EV manufacturers"
            """)
            
    elif st.session_state.active_tab == "Overview":
        show_overview(data)
    elif st.session_state.active_tab == "Company Analysis":
        show_company_analysis(data, sp500_companies)
    elif st.session_state.active_tab == "Sector Trends":
        show_sector_trends(data)
    elif st.session_state.active_tab == "Suggest a Company":
        suggest_company()

    # Add footer with additional resources
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📚 Resources**")
        st.markdown("- [Investment Basics]()")
        st.markdown("- [Market Analysis Guide]()")
    with col2:
        st.markdown("**🔗 Quick Links**")
        st.markdown("- [Top Companies]()")
        st.markdown("- [Sector Overview]()")
    with col3:
        st.markdown("**💡 Tips**")
        st.markdown("- Ask specific questions")
        st.markdown("- Compare multiple companies")

if __name__ == "__main__":
    main()
