#PART 3

#import the needed libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path


#configuration of the page, with its title and icon
st.set_page_config(page_title="Financial Transactions Time Analysis Dashboard",page_icon="📈",layout="wide")

#definition of the color and template to use throughout the page
PRIMARY="#1f4e79"

PLOT_TEMPLATE="simple_white"

#loading of the data
#using the @st.cache_data to avoid reloading or recomputing every time the app reruns
@st.cache_data
def load_data():

    #read the csv file of the denormalized table creater in the previous analysis and save it into df
    BASE_DIR = Path(__file__).resolve().parent
    df = pd.read_csv(BASE_DIR/"fact_enriched.csv")

    #creation of the column date by combining the columns year, month and date
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])

    return df

df=load_data()


#STRUCTURE OF THE PAGE

#selecting a title for the dashboard
st.title("📈 Financial Transactions Dashboard")

#adding a short description of the dashboard
st.subheader("Interactive dashboard for the analysis of financial transactions during 2024.")

#setting a divider line
st.divider()




#FILTERING ACCORDING TO THE DATE

#adding a subtitle for the date filter 
st.subheader("Date Filter")

#setting the default values for the starting date and ending date
default_start=pd.Timestamp("2024-01-01")
default_end=pd.Timestamp("2024-12-31")

#creating a selector for the interval of time
date_range=st.date_input("Select period",[default_start, default_end])

#checking if both initial and ending dates have been selected
if len(date_range)==2:

    #converting dates in timestamp format
    start_date=pd.Timestamp(date_range[0])
    end_date=pd.Timestamp(date_range[1])

#if the user does not choose any date just use the default ones
else:

    start_date=default_start
    end_date=default_end

#filtering the dataset by maintaining only the rows in the chosen time interval
df_filtered = df[(df["date"] >= start_date) &(df["date"] <= end_date)]



#add another divider line
st.divider()



#COMPUTING SOME RELEVANT KPIs REGARDING THE TIME ANALYSIS

#how many buy transactions in the chosen timeframe
buy_count=(df_filtered["transaction_type"].eq("BUY").sum())

#how many sell transactions in the chosen timeframe
sell_count=(df_filtered["transaction_type"].eq("SELL").sum())

#total number of transactions in the chosen timeframe
total_transactions=len(df_filtered)

#total number of different symbols in the chosen timeframe
distinct_symbols=df_filtered["symbol"].nunique()


#adding a title for the KPI's section
st.subheader("Key Performance indicators")

#creation of the 4 columns for the KPIs
kpi1,kpi2,kpi3,kpi4=st.columns(4)

#adding KPIs in the dashboard
kpi1.metric("TOTAL TRANSACTIONS",f"{total_transactions:,}")

kpi2.metric("BUY",f"{buy_count:,}")

kpi3.metric("SELL",f"{sell_count:,}")

kpi4.metric("SYMBOLS",f"{distinct_symbols}")


#putting a divider line
st.divider()




#FIRST CHART: LINE CHART FOR TOTAL TRANSACTIONS

#setting a title for the graph
st.subheader("Transaction Volume Trend")

#grouping the transactions by day and counting them
tx_day=(df_filtered.groupby("date").size().reset_index(name="transactions"))

#creation of the line chart
#putting on x-axis the date and on y-axis the number of transactions per day
fig=px.line(tx_day,x="date",y="transactions",template=PLOT_TEMPLATE)

#personalizing the line chart
fig.update_layout(height=350,showlegend=False,xaxis_title="Date",yaxis_title="Transactions",font=dict(size=14),
                  margin=dict(l=20,r=20,t=20,b=20))

#setting the color and the line width
fig.update_traces(line=dict(color=PRIMARY,width=3))

#adding a horizontal, grey grid 
fig.update_yaxes(showgrid=True,gridcolor="rgba(180,180,180,0.2)")

#plotting the chart on the dashboard
st.plotly_chart(fig,use_container_width=True)

#adding some relevant information about the peak trading day in a lower section
peak_idx=tx_day.loc[tx_day["transactions"].idxmax()]
peak_day=peak_idx["date"]
peak_value=peak_idx["transactions"]

st.markdown(f"### Key Insights (**{start_date.strftime('%d %b %Y')}** - **{end_date.strftime('%d %b %Y')}**)")

st.write(f"""The peak trading day is **{peak_day.strftime('%d %b %Y')}**, with a total of **{peak_value}** transactions (BUY+SELL).""")


#adding a divider line
st.divider()



#LOWER PAGE SECTIONS
st.subheader("Market Breakdown")

#SETTING THE PAGE FOR THE LOWER GRAPHS
#the lower part of the page gets divided into 3 columns
col1, col2, col3=st.columns(3)


#SECOND CHART: TOP3 SYMBOLS

#insert the chart in the first column of the lower part of the page
with col1:

    #setting the title of the graph
    st.subheader("Top 3 Symbols")

    #finding the most frequent 3 symbols
    top_symbols=(df_filtered["symbol"].value_counts().head(3).reset_index())

    #rename the columns
    top_symbols.columns=["symbol","transactions"]

    #creating a barchart
    fig=px.bar(top_symbols,x="symbol",y="transactions",text="transactions",template=PLOT_TEMPLATE)

    #personalizing the barchart
    fig.update_layout(showlegend=False,xaxis_title="Symbol",yaxis_title="Transactions",height=350,
                      margin=dict(l=10,r=10,t=20,b=10))

    #setting the color of the chart
    fig.update_traces(marker_color=PRIMARY)

    #adding a horizontal, grey grid
    fig.update_yaxes(showgrid=True,gridcolor="rgba(180,180,180,0.2)")

    #plotting the chart
    st.plotly_chart(fig,use_container_width=True)




#THIRD CHART: TOP5 SECTORS

#insert the chart in the second column of the lower part of the page
with col2:

    #giving a title to the chart
    st.subheader("Top 5 Sectors")

    #find the top5 sectors in terms of number of transactions
    top_sector=(df_filtered["sector"].value_counts().head(5).sort_values().reset_index())

    #renaming the columns
    top_sector.columns=["sector","transactions"]

    #creation of a horizontal barchart
    fig=px.bar(top_sector,x="transactions",y="sector",orientation="h",text="transactions",template=PLOT_TEMPLATE)

    #setting the features of the barchart
    fig.update_layout(height=350,showlegend=False,xaxis_title="Transactions",yaxis_title="Sector",
                      margin=dict(l=10,r=10,t=20,b=10))

    #setting the color of the barchart
    fig.update_traces(marker_color=PRIMARY)

    #adding a grey, vertical grid
    fig.update_xaxes(showgrid=True,gridcolor="rgba(180,180,180,0.2)")

    #plotting the barchart
    st.plotly_chart(fig,use_container_width=True)


#FOURTH CHART: TOP5 INDUSTRIES

#insert the chart in the third column of the lower part of the page
with col3:

    #giving a name to the chart
    st.subheader("Top 5 Industries")

    #find the 5 most present industries
    top_industry=(df_filtered["industry"].value_counts().head(5).sort_values().reset_index())

    #setting the names of the columns
    top_industry.columns=["industry","transactions"]

    #creation of the horizontal barchart
    fig=px.bar(top_industry,x="transactions",y="industry",orientation="h",text="transactions",template=PLOT_TEMPLATE)

    #personalizing the features of the barchart
    fig.update_layout(height=350,showlegend=False,xaxis_title="Transactions",yaxis_title="Industry",
                      margin=dict(l=10,r=10,t=20,b=10))

    #setting the colour of the chart
    fig.update_traces(marker_color=PRIMARY)

    #adding a vertical grid
    fig.update_xaxes(showgrid=True,gridcolor="rgba(180,180,180,0.2)")

    #plotting the chart
    st.plotly_chart(fig,use_container_width=True)


#adding a final description of the previously found results

#finding the top symbol and its value
symbol_counts=df_filtered["symbol"].value_counts()
top_symbol=symbol_counts.index[0]
symbol_value=symbol_counts.iloc[0]

#finding the top sector and its value
sector_counts=df_filtered["sector"].value_counts()
top_sector=sector_counts.index[0]
sector_value=sector_counts.iloc[0]

#finding the top industry and its value
industry_counts=df_filtered["industry"].value_counts()
top_industry=industry_counts.index[0]
industry_value=industry_counts.iloc[0]

#writing the results on the bottom of the page, in a dedicated section
st.markdown(f"### Key Insights (**{start_date.strftime('%d %b %Y')}** - **{end_date.strftime('%d %b %Y')}**)")

st.write(f"""
- The most traded symbol is **{top_symbol}** with **{symbol_value}** transactions.
- The dominant sector is **{top_sector}** with **{sector_value}** transactions.
- The dominant industry is **{top_industry}** with **{industry_value}** transactions.
""")


#adding a new divider line
st.divider()

#adding a caption at the end of the dashboard
st.caption("Financial Transactions Dashboard")