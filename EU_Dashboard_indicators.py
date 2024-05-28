import streamlit as st
import pandas as pd
import plotly.express as px
from pandas_datareader import wb
import datetime

# Initialize data
eu_countries = [
    'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR',
    'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL',
    'PT', 'RO', 'SE', 'SI', 'SK'
]

indicator = {
    'SP.POP.TOTL': 'Total Population',
    'NY.GDP.MKTP.CD': 'GDP (USD)',
    'NY.GDP.DEFL.KD.ZG': 'Inflation (Annual %)',
    'SP.DYN.LE00.IN': 'Life Expectancy (Years)',
    'NE.EXP.GNFS.CD': 'Exports (USD)'
}

start_date = datetime.datetime(1999, 1, 1)
end_date = datetime.datetime(2022, 1, 1)

df = wb.download(indicator=indicator.keys(), country=eu_countries, start=start_date, end=end_date)
df.rename(columns=indicator, inplace=True)
df.reset_index(inplace=True)
df['year'] = df['year'].astype(int)
df.sort_values(by=['country', 'year'], inplace=True)

# Streamlit layout
st.set_page_config(page_title="EU Indicator Dashboard", layout="wide")

with st.sidebar:
    st.title('EU Indicator Dashboard')
    indicator_selection = st.selectbox('Select an Indicator', list(indicator.values()))
    selected_year = st.selectbox('Select a Year', options=sorted(df['year'].unique()))

# Filter data
df_selected = df[df['year'] == selected_year]
df_selected_sorted = df_selected.sort_values(by=indicator_selection, ascending=False)
df_selected_sorted[indicator_selection] = df_selected_sorted[indicator_selection].round(2)

# Map
fig_map = px.choropleth(df_selected, locations='country', color=indicator_selection,
                    color_continuous_scale='blues',
                    labels={indicator_selection: indicator_selection},
                    title=f"{indicator_selection} in {selected_year}",
                    locationmode='country names')
fig_map.update_geos(projection_type="natural earth", scope="europe")
fig_map.update_layout(template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=30, b=0),  # Adjust margin to show title
        height=500)  # Adjust height as necessary

# Calculate the sum of the selected indicator for the top 10 countries
top_countries = df_selected_sorted.head(10)
total = top_countries[indicator_selection].sum()

# Calculate percentages
top_countries['Percentage'] = (top_countries[indicator_selection] / total * 100)

# Pie chart with percentages
if indicator_selection in ['Total Population', 'Exports (USD)', 'GDP (USD)']:
    top_countries = df_selected_sorted.head(27)
    total = top_countries[indicator_selection].sum()
    top_countries['Percentage'] = (top_countries[indicator_selection] / total * 100).round(2)
    fig_pie = px.pie(top_countries, values='Percentage', names='country', hole=0.5,
                     title=f"Percentage of {indicator_selection} in EU Countries")
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
else:
    fig_pie = px.bar(df_selected_sorted, x='country', y=indicator_selection,
                     title=f"{indicator_selection} for EU Countries in {selected_year}",
                     labels={indicator_selection: f"{indicator_selection} ({selected_year})"})

# Filter data for selected year
df_selected = df[df['year'] == selected_year]

# Calculate average of the selected indicator
average_value = df_selected[indicator_selection].mean()

def format_number(num):
    """Formats a number with M or B as a suffix."""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    else:
        return str(num.round(2))


if selected_year > 1999:
    previous_year_data = df[df['year'] == selected_year - 1]
    previous_year_avg = previous_year_data[indicator_selection].mean()
    percentage_change = str((((average_value - previous_year_avg) / previous_year_avg) * 100).round(2))+'%'
else:
    percentage_change = "N/A"

# Display the layout in 2 columns
col1, col2 = st.columns([1.25, 3], gap='medium')

with col1:
    st.markdown(f'#### Average {indicator_selection}')
    st.metric(label=f"Average in {selected_year}", value=format_number(average_value))
    st.markdown(f'#### Change in average {indicator_selection}')
    st.metric(label=f"Average change from {selected_year-1} to {selected_year}", value=percentage_change)
    st.subheader('Top Countries')
    st.dataframe(df_selected_sorted[['country', indicator_selection]].head(10))

with col2:
    st.markdown(f'#### {indicator_selection} Map')
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown(f'#### {indicator_selection} Distribution')
    st.plotly_chart(fig_pie, use_container_width=True)

# About
with st.expander('About', expanded=True):
    st.write('''
        - Data Source: [World Bank](https://worldbank.org).
        - The dashboard visualizes key indicators for EU countries.
    ''')