import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Main function to run the Streamlit app
def main():
    st.title("Investment Analysis Dashboard")

    # Load data
    data = load_data("./investment_analysis_results_claude3_20241019_031757.json")

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Overview", "Company Analysis", "Sector Analysis", "Trends"])

    if page == "Overview":
        show_overview(data)
    elif page == "Company Analysis":
        show_company_analysis(data)
    elif page == "Sector Analysis":
        show_sector_analysis(data)
    elif page == "Trends":
        show_trends(data)

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
    st.subheader("Top 10 Companies by Ultimate Strength")
    top_10 = df.nlargest(10, 'ultimate_strength')[['company', 'ultimate_strength', 'recommendation']]
    st.table(top_10)

def search_companies(search_term, companies):
    return [company for company in companies if search_term.lower() in company.lower()]

def display_company_info(company_data, company_name):
    st.subheader(f"{company_name} Analysis")
    st.write(f"Recommendation: {company_data['recommendation']}")
    st.write(f"Ultimate Strength: {company_data['ultimate_strength']}")

    # Create a radar chart for the scores
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

    st.subheader("Explanation")
    st.write(company_data['explanation'])

def show_company_analysis(data):
    st.header("Company Analysis")

    companies = list(data['company_analysis'].keys())

    # Add a search bar
    search_term = st.text_input("Search for a company", "")

    if search_term:
        search_results = search_companies(search_term, companies)
        if search_results:
            selected_company = st.selectbox("Select a company from search results", search_results)
            company_data = data['company_analysis'][selected_company]
            display_company_info(company_data, selected_company)
        else:
            st.warning("No companies found matching your search term.")
    else:
        # If no search term, show the dropdown with all companies
        selected_company = st.selectbox("Or select a company from the list", companies)
        company_data = data['company_analysis'][selected_company]
        display_company_info(company_data, selected_company)

    # Add a section for company comparison
    st.subheader("Company Comparison")
    companies_to_compare = st.multiselect("Select companies to compare", companies)
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

def show_sector_analysis(data):
    st.header("Sector Analysis")

    # You'll need to add sector information to your data for this to work
    # For now, we'll just show a placeholder
    st.write("Sector analysis will be implemented here.")

def show_trends(data):
    st.header("Market Trends")

    # Display the consolidated trends
    for sector, trend in data['consolidated_trends'].items():
        st.subheader(sector)
        st.write(trend)

if __name__ == "__main__":
    main()
