import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

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

def main():
    st.set_page_config(layout="wide")  # Use wide layout for better space utilization
    
    # Initialize session state for navigation
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'selected_sector' not in st.session_state:
        st.session_state.selected_sector = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Overview"

    st.title("Investment Analysis Dashboard")

    # Load data
    data = load_data()
    sp500_df = load_sp500_data()
    sp500_companies = set(sp500_df['name'].apply(normalize_company_name))

    # Custom navigation bar using buttons
    st.sidebar.title("Navigation")
    if st.sidebar.button("Overview"):
        st.session_state.active_tab = "Overview"
    if st.sidebar.button("Company Analysis"):
        st.session_state.active_tab = "Company Analysis"
    if st.sidebar.button("Sector Trends"):
        st.session_state.active_tab = "Sector Trends"
    if st.sidebar.button("Suggest a Company"):
        st.session_state.active_tab = "Suggest a Company"

    # Render content based on active tab
    if st.session_state.active_tab == "Overview":
        show_overview(data)
    elif st.session_state.active_tab == "Company Analysis":
        show_company_analysis(data, sp500_companies)
    elif st.session_state.active_tab == "Sector Trends":
        show_sector_trends(data)
    elif st.session_state.active_tab == "Suggest a Company":
        suggest_company()

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

    # Displaying company details and earnings information
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

    # Add explanation section back
    st.subheader("Analysis Explanation")
    explanation = company_data.get('explanation', 'N/A')
    st.write(explanation)

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

if __name__ == "__main__":
    main()
