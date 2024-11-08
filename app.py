import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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

def main():
    st.title("Investment Analysis Dashboard")

    # Load data
    data = load_data()
    sp500_df = load_sp500_data()
    sp500_companies = set(sp500_df['name'].apply(normalize_company_name))

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Overview", "Company Analysis", "Sector Trends", "Suggest a Company"])

    if page == "Overview":
        show_overview(data)
    elif page == "Company Analysis":
        show_company_analysis(data, sp500_companies)
    elif page == "Sector Trends":
        show_trends(data)
    elif page == "Suggest a Company":
        suggest_company()

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

    # Top 10 companies by ultimate strength
    st.subheader("Top 50 Companies by Ultimate Strength")
    top_10 = df.nlargest(50, 'ultimate_strength')[['company', 'ultimate_strength', 'recommendation']]
    st.table(top_10)

def search_companies(search_term, companies):
    return [company for company in companies if search_term.lower() in company.lower()]

def display_company_info(company_data, company_name):
    st.subheader(f"{company_name} Analysis")
    
    # Access keys with safeguards
    recommendation = company_data.get('recommendation', 'N/A')
    ultimate_strength = company_data.get('ultimate_strength', 'N/A')
    industry = company_data.get('industry', 'N/A')
    market_cap = company_data.get('market_cap', 'N/A')
    country = company_data.get('country', 'N/A')
    website = company_data.get('website', 'N/A')
    
    # Display company info
    st.write(f"Recommendation: {recommendation}")
    st.write(f"Ultimate Strength: {ultimate_strength}")
    st.write(f"Industry: {industry}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"Country: {country}")
    if website != 'N/A':
        st.write(f"Website: [Link]({website})")
    else:
        st.write(f"Website: {website}")

    # Debugging output: Print keys of company_data to identify missing fields
    # st.write("Debug Info: Available Keys in company_data")
    # st.write(list(company_data.keys()))

    # Create a radar chart for the scores if they exist
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

    # Explanation if it exists
    explanation = company_data.get('explanation', 'N/A')
    st.subheader("Explanation")
    st.write(explanation)


def show_company_analysis(data, sp500_companies):
    st.header("Company Analysis")

    companies = list(data['company_analysis'].keys())

    # Add search and filter options
    search_term = st.text_input("Search for a company or symbol", "").lower()
    filter_sp500 = st.checkbox("Show only S&P 500 companies")

    # Filter companies by S&P 500 membership
    filtered_companies = [
        company for company in companies
        if (not filter_sp500 or normalize_company_name(company) in sp500_companies)
        and (search_term in company.lower() or any(search_term in symbol.lower() for symbol in data['company_analysis'][company]['symbols'].split(',')))
    ]

    if filtered_companies:
        selected_company = st.selectbox("Select a company from the list", filtered_companies)
        company_data = data['company_analysis'][selected_company]
        display_company_info(company_data, selected_company)
    else:
        st.warning("No companies found matching your search term.")

    # Add a section for company comparison
    st.subheader("Company Comparison")
    companies_to_compare = st.multiselect("Select companies to compare", filtered_companies)
    if len(companies_to_compare) > 1:
        comparison_data = {company: data['company_analysis'][company] for company in companies_to_compare}
        show_company_comparison(comparison_data)

def show_company_comparison(comparison_data):
    # Create a DataFrame for easy comparison
    df = pd.DataFrame({company: {**data['scores'], 'Ultimate Strength': data['ultimate_strength']} 
                       for company, data in comparison_data.items()}).T

    # Display the comparison table
    st.write(df)

    # Create a radar chart for comparison
    fig = go.Figure()

    for company in comparison_data.keys():
        fig.add_trace(go.Scatterpolar(
            r=list(comparison_data[company]['scores'].values()) + [comparison_data[company]['ultimate_strength']],
            theta=list(comparison_data[company]['scores'].keys()) + ['Ultimate Strength'],
            fill='toself',
            name=company
        ))

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, max(max(company['scores'].values()) for company in comparison_data.values()) + 5]
        )),
      showlegend=True
    )

    st.plotly_chart(fig)

def show_trends(data):
    st.header("Market Trends")

    # Get list of sectors
    sectors = list(data['consolidated_trends'].keys())

    # Search and Filter
    search_term = st.text_input("Search for a sector", "").lower()
    filtered_sectors = [sector for sector in sectors if search_term in sector.lower()]

    # Display results
    if filtered_sectors:
        for sector in filtered_sectors:
            st.subheader(sector.capitalize())
            st.write(data['consolidated_trends'][sector])
    else:
        st.warning("No sectors found matching your search term.")

def suggest_company():
    st.header("Suggest a Company for Analysis")
    suggested_company = st.text_input("Enter the name or symbol of a company that you think should be analyzed")

    if suggested_company:
        st.write(f"Thanks! We'll consider adding '{suggested_company}' to the analysis in the future.")
        # Here you could add functionality to save this suggestion to a file or database for later processing.

if __name__ == "__main__":
    main()
