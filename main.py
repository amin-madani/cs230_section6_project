
"""
Name:       Amin Madani
CS230:      Section 006
Data:       Nuclear Explosions 1945-1998 (2046 rows)
URL:        

Description:    

1) The dashboard analyzes nuclear explosions globally from 1945 to 1998 and give insights into detonation trends and locations.
2) Filters include deployment location, year range, yield range, and depth for focused exploration.
3) Visualizations include bar charts, scatter plots, line charts, pie charts, and an interactive geographical map.
4) A sortable table ranks explosions by average yield, while a pivot table highlights counts by purpose and location.
5) Cleaned and processed data ensures accuracy, with features like yield intensity-based mapping and detailed tooltips.
6) Users can download filtered datasets as CSV for further analysis.

"""


# Import libraries
import pandas as pd
import numpy as np
import streamlit as st
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from streamlit_folium import st_folium
import folium
import pydeck as pdk

# Page Design Features
st.set_page_config(page_title="Nuclear Explosions Analysis", layout="wide")
st.markdown(
    """
     <div style="background-color:#FF4B4B;padding:15px;border-radius:10px">
        <h2 style="color:white;text-align:center;">Nuclear Explosions Analysis (1945-1998): Insights into Global Detonations</h2>
    </div>
    <style>
    body {
        background-color: #ffe6e6; 
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    h1 {
        color: #003366;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.image("header_image.jpg", use_container_width=True)

# Load dataset
try:
    df = pd.read_excel("nuclear_explosions.xlsx")
except FileNotFoundError:
    st.error("The data file could not be found.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.stop()

# Check for missing values
df.isnull().sum()

# Remove Nan values
df.replace("Nan", pd.NA, inplace=True)
df.dropna(inplace=True)

# Rename columns using a dictionary
df = df.rename(
    columns={
        "Data.Source": "Source",
        "Location.Cordinates.Latitude": "Latitude",
        "Location.Cordinates.Longitude": "Longitude",
        "Data.Magnitude.Body": "Magnitude_Body",
        "Data.Magnitude.Surface": "Magnitude_Surface",
        "Location.Cordinates.Depth": "Depth",
        "Data.Yeild.Lower": "Yeild_Lower",
        "Data.Yeild.Upper": "Yeild_Upper",
        "Data.Purpose": "Purpose",
        "Data.Name": "Name",
        "Data.Type": "Type",
        "Date.Day": "Day",
        "Date.Month": "Month",
        "Date.Year": "Year",
    }
)

# Dictionary to map misspelled names to the correct ones
location_corrections = {
    "Amchitka Ak": "Amchitka",
    "Arkhan Russ": "Arkhangelsk",
    "Astrak Russ": "Astrakhan",
    "Azgie Kazakh": "Azgir",
    "Azgir Kazakh": "Azgir",
    "Bashki Russ": "Bashkiria",
    "Bashkir Russ": "Bashkiria",
    "C. Nevada": "Central Nevada",
    "Carlsbad Nm": "Carlsbad",
    "Chita Russ": "Chita",
    "Christmas Is": "Christmas Island",
    "Emu Austr": "Emu",
    "Fallon Nv": "Fallon",
    "Fangataufa": "Fangataufa",
    "Fangataufaa": "Fangataufa",
    "Farmingt Nm": "Farmington",
    "Grand V Co": "Grand Valley",
    "Hattiesb Ms": "Hattiesburg",
    "Hattiese Ms": "Hattiesburg",
    "Htr Russ": "Hitler Region",
    "Hururoa": "Mururoa",
    "In Ecker Alg": "In Ekker",
    "Irkuts Russ": "Irkutsk",
    "Jakuts Ruse": "Yakutsk",
    "Jakuts Russ": "Yakutsk",
    "Johnston Is": "Johnston Island",
    "Kalmyk Russ": "Kalmykia",
    "Kazakh": "Kazakhstan",
    "Kazakhstan": "Kazakhstan",
    "Kemero Russ": "Kemerovo",
    "Komi Russ": "Komi",
    "Krasno Russ": "Krasnoyarsk",
    "Kz Russ": "Kazakhstan",
    "Malden Is": "Malden Island",
    "Mangy Kazakh": "Mangyshlak",
    "Marali Austr": "Maralinga",
    "Mary Turkmen": "Mary",
    "Mellis Nv": "Mellis",
    "Monteb Austr": "Monte Bello",
    "Mtr Russ": "Murmansk",
    "Mueueoa": "Mururoa",
    "Murm Russ": "Murmansk",
    "Murueoa": "Mururoa",
    "Muruhoa": "Mururoa",
    "Mururoa": "Mururoa",
    "N2 Russ": "N2 Region",
    "Nellis Nv": "Nellis",
    "Nz Russ": "New Zealand Region",
    "Offuswcoast": "Off US West Coast",
    "Orenbg Russ": "Orenburg",
    "Pamuk Uzbek": "Pamuk",
    "Perm Russ": "Perm",
    "Reggane Alg": "Reggane",
    "Rifle Co": "Rifle",
    "S. Atlantic": "South Atlantic",
    "S.Atlantic": "South Atlantic",
    "Semi Kazakh": "Semipalatinsk",
    "Stavro Russ": "Stavropol",
    "Tuymen Russ": "Tyumen",
    "Tyumen Russ": "Tyumen",
    "Ukeaine": "Ukraine",
    "Uzbek": "Uzbekistan",
    "W Kazakh": "West Kazakhstan",
    "W Mururoa": "West Mururoa",
    "Wsw Mururoa": "West-Southwest Mururoa",
}

# Apply corrections to the column
df["WEAPON DEPLOYMENT LOCATION"] = df["WEAPON DEPLOYMENT LOCATION"].replace(location_corrections)

# Dictionary to map purpose abbreviations to full descriptions
purpose_descriptions = {
    "Combat": "Combat Detonation",
    "Fms": "Function Material Study",
    "Fms/Wr": "Function Material Study and Weapon-Related",
    "Me": "Military Exercise",
    "Nan": "Unknown Purpose",
    "Pne": "Peaceful Nuclear Explosion",
    "Pne/Wr": "Peaceful Nuclear Explosion and Weapon-Related",
    "Pne:Plo": "Peaceful Nuclear Explosion for Plowshare Program",
    "Pne:V": "Peaceful Nuclear Explosion for Venting",
    "Sam": "Subatomic Measurement",
    "Sb": "Safety Burst",
    "Se": "Structural Engineering",
    "Se/Wr": "Structural Engineering and Weapon-Related",
    "Transp": "Transportation Testing",
    "We": "Weapon Experimentation",
    "We/Sam": "Weapon Experimentation and Subatomic Measurement",
    "We/Wr": "Weapon Experimentation and Weapon-Related",
    "Wr": "Weapon-Related",
    "Wr/F/S": "Weapon-Related Function Study",
    "Wr/F/Sa": "Weapon-Related Function Study with Safety Analysis",
    "Wr/Fms": "Weapon-Related Function Material Study",
    "Wr/P/S": "Weapon-Related with Peaceful and Safety Analysis",
    "Wr/P/Sa": "Weapon-Related with Peaceful and Safety Analysis",
    "Wr/Pne": "Weapon-Related Peaceful Nuclear Explosion",
    "Wr/Sam": "Weapon-Related Subatomic Measurement",
    "Wr/Se": "Weapon-Related Structural Engineering",
    "Wr/We": "Weapon-Related Weapon Experimentation",
    "Wr/We/S": "Weapon-Related Weapon Experimentation with Safety Analysis",
}

# Apply mapping to the Purpose column
df["Purpose"] = df["Purpose"].replace(purpose_descriptions)

# Dictionary to map abbreviations or inconsistent values to standardized full names
type_corrections = {
    "Airdrop": "Airdrop",
    "Atmosph": "Atmospheric",
    "Balloon": "Balloon",
    "Barge": "Barge",
    "Crater": "Crater",
    "Gallery": "Gallery",
    "Mine": "Mine",
    "Rocket": "Rocket",
    "Shaft": "Shaft",
    "Shaft/Gr": "Shaft Ground-Based",
    "Shaft/Lg": "Shaft Large",
    "Ship": "Ship-Based",
    "Space": "Space-Based",
    "Surface": "Surface",
    "Tower": "Tower",
    "Tunnel": "Tunnel",
    "Ug": "Underground",
    "Uw": "Underwater",
    "Water Su": "Water Surface",
    "Watersur": "Water Surface",
}

# Apply mapping to the Type column
df["Type"] = df["Type"].replace(type_corrections)

# Normalize capitalization 
df["Type"] = df["Type"].str.title()



# Add calculated columns
df["Magnitude_Category"] = df["Magnitude_Body"].apply(
    lambda x: "High" if x > 5 else ("Moderate" if x > 3 else "Low")
)
df["Date"] = pd.to_datetime(df[["Day", "Month", "Year"]])
df["Week_of_Year"] = df["Date"].dt.isocalendar().week

# Sidebar Filters
st.sidebar.title("Filter Options")
locations = df["WEAPON DEPLOYMENT LOCATION"].dropna().unique()
select_location = st.sidebar.multiselect("Select Deployment Location", locations, default=["Hiroshima", "In Ekker", "Pokhran","Monte Bello", "Emu"])

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
year_range = st.sidebar.slider("Year Range", year_min, year_max, (year_min, year_max))

yield_min = int(df["Yeild_Lower"].min())
yield_max = int(df["Yeild_Lower"].max())
yield_range = st.sidebar.slider("Yield Range", yield_min, yield_max, (yield_min, yield_max))

depth_selection = ["Above Ground", "Underground", "All"]
select_depth = st.sidebar.radio("Select Depth", depth_selection, index=2)

# Filtering function with default parameter
def filter_data(df, location, year_range, yield_range, depth="All"):
    filtered_data = df[df["WEAPON DEPLOYMENT LOCATION"].isin(location)]
    filtered_data = filtered_data[
        (filtered_data["Year"] >= year_range[0]) & (filtered_data["Year"] <= year_range[1])
    ]
    filtered_data = filtered_data[
        (filtered_data["Yeild_Lower"] >= yield_range[0]) & (filtered_data["Yeild_Lower"] <= yield_range[1])
    ]
    if depth != "All":
        if depth == "Above Ground":
            filtered_data = filtered_data[filtered_data["Depth"] < 0]
        elif depth == "Underground":
            filtered_data = filtered_data[filtered_data["Depth"] > 0]
    return filtered_data

filtered_data = filter_data(df, select_location, year_range, yield_range, select_depth)

# Sorting functionality
sorted_data = filtered_data.sort_values(by="Yeild_Upper", ascending=False)

# Table: Explosions Sorted by Average Yield for Selected Deployment Locations
st.subheader("Quick View for Explosions")

if filtered_data.empty:
    st.write("No Data Available")
else:
    # Compute Average Yield
    filtered_data["Avg_Yield"] = (filtered_data["Yeild_Lower"] + filtered_data["Yeild_Upper"]) / 2

    # Select relevant columns and sort by Avg_Yield in descending order
    sorted_yields = filtered_data[["Name", "Avg_Yield", "Magnitude_Category", "WEAPON SOURCE COUNTRY"]].sort_values(
        by="Avg_Yield", ascending=False
    ).rename(columns={
        "Name": "Explosion Name",
        "Avg_Yield": "Average Yield (kt)",
        "Magnitude_Category": "Magnitude Category",
        "WEAPON SOURCE COUNTRY": "Country"
    })

    
    st.write(sorted_yields)


# Pivot Table: Count of Explosions by Purpose and Location
st.subheader("Count of Explosions by Purpose and Location")

if filtered_data.empty:
    st.write("No Data Available")
else:
    pivot_table = pd.pivot_table(
        filtered_data,
        values="Name",  
        index="Purpose",  
        columns="WEAPON DEPLOYMENT LOCATION",  
        aggfunc="count",  
        fill_value=0  
    )

    
    st.write(pivot_table)

# Visualizations
st.subheader("Number of Nuclear Explosions by Deployment Location")
if filtered_data.empty:
    st.write("No Data Available")
else:
    location_count = filtered_data["WEAPON DEPLOYMENT LOCATION"].value_counts()
    fig, ax = plt.subplots()
    location_count.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_ylabel("Number of Explosions")
    
    st.pyplot(fig)

# Scatter Plot: Yield of Nuclear Explosions Over Time
st.subheader("Yield of Nuclear Explosions Over Time")

if filtered_data.empty:
    st.write("No Data Available")
else:
    # Group data by location
    fig, ax = plt.subplots(figsize=(10, 6))
    for location, group in filtered_data.groupby("WEAPON DEPLOYMENT LOCATION"):
        ax.scatter(
            group["Year"],
            group["Yeild_Upper"],
            label=location,
            alpha=0.7,
            s=50  
        )
    
    
    ax.set_xlabel("Year", fontsize=14)
    ax.set_ylabel("Yield Upper (kt)", fontsize=14)
    ax.legend(title="Deployment Location", loc="upper left", bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle='--', alpha=0.6)
    
    
    st.pyplot(fig)

# Line Chart: Yearly Trend of Explosion Counts by Country
st.subheader("Yearly Trend of Explosion Counts by Country")

if filtered_data.empty:
    st.write("No Data Available")
else:
    
    yearly_counts = (
        filtered_data.groupby(["Year", "WEAPON SOURCE COUNTRY"])
        .size()
        .reset_index(name="Counts")
    )

    # Create the line chart
    fig, ax = plt.subplots(figsize=(10, 6))
    for country, group in yearly_counts.groupby("WEAPON SOURCE COUNTRY"):
        ax.plot(
            group["Year"],
            group["Counts"],
            label=country,
            marker="o",  
            linewidth=2,
        )

    # Customize the chart
    ax.set_xlabel("Year", fontsize=14)
    ax.set_ylabel("Number of Explosions", fontsize=14)
    ax.legend(title="Country", fontsize=10, loc="upper left", bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle="--", alpha=0.6)

    # Display the chart in Streamlit
    st.pyplot(fig)



# Pie Chart: Distribution of Explosions by Country
st.subheader("Distribution of Explosions by Country")

if filtered_data.empty:
    st.write("No Data Available")
else:
    country_count = filtered_data["WEAPON SOURCE COUNTRY"].value_counts()

    # Calculate percentages for the legend
    total_explosions = country_count.sum()
    legend_labels = [
        f"{country}: {count}, {count / total_explosions * 100:.1f}%" 
        for country, count in zip(country_count.index, country_count.values)
    ]

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts = ax.pie(
        country_count.values,
        labels=None,  
        startangle=90,      
        colors=plt.cm.tab10.colors,  
        textprops={'fontsize': 10},  
    )

    # Add a legend for the country names with counts and percentages
    ax.legend(
        wedges,
        legend_labels,
        title="Country (Count, Percentage)",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=10
    )

    
    st.pyplot(fig)





# Geographical Distribution of Nuclear Explosions
st.subheader("Geographical Distribution of Nuclear Explosions")

if filtered_data.empty:
    st.write("No Data Available")
else:
    # Compute the average yield
    filtered_data["Avg_Yield"] = (filtered_data["Yeild_Lower"] + filtered_data["Yeild_Upper"]) / 2

    # Normalize yield for color intensity
    norm = mcolors.Normalize(vmin=filtered_data["Avg_Yield"].min(), vmax=filtered_data["Avg_Yield"].max())
    cmap = plt.cm.get_cmap("PiYG_r") 

    # Function to convert normalized yield to hex color
    def yield_to_color(yield_value):
        rgba = cmap(norm(yield_value))  
        return mcolors.to_hex(rgba)  

    # Map initialization
    map_center = [20, 0]
    m = folium.Map(location=map_center, zoom_start=2, tiles="CartoDB positron")

    # Add markers to the map
    for _, row in filtered_data.iterrows():
        avg_yield = row["Avg_Yield"]
        weapon_type = row["Type"]
        country = row["WEAPON SOURCE COUNTRY"]
        location = row["WEAPON DEPLOYMENT LOCATION"]

        # Add CircleMarker
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=7,  
            color=yield_to_color(avg_yield),  
            fill=True,
            fill_opacity=0.7,
            tooltip=(
                f"<b>Type:</b> {weapon_type}<br>"
                f"<b>Country:</b> {country}<br>"
                f"<b>Avg Yield:</b> {avg_yield:.2f} kt<br>"
                f"<b>Location:</b> {location}"
            ),
        ).add_to(m)

    
    st_folium(m, width=700, height=500)


# Download CSV
csv = filtered_data.to_csv(index=False)
st.download_button(
    "Download Filtered Data as CSV", data=csv, file_name="Filtered_Data.csv", mime="text/csv"
)
