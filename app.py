import matplotlib
matplotlib.use("TkAgg") 
import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import numpy as np
from streamlit_folium import folium_static
from weather import get_weather
from database import insert_weather_data

# 📌 MySQL Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "weather_user",
    "password": "weather_pass",
    "database": "weather_db"
}

# 🌤️ Weather Dashboard Title
st.title("🌤️ Weather Dashboard with City-Based Analysis")

# 🔍 Search Box for City Input
city_name = st.text_input("🔍 Search city", placeholder="Enter city name...")
state_name = st.text_input("🏩 Enter state (optional)", placeholder="Enter state name...")

if city_name:
    if st.button("Get Weather Data"):
        weather_info = get_weather(city_name, state_name)

        if weather_info:
            insert_weather_data(weather_info)
            st.success("✅ Weather data saved successfully!")

            # 🌡 Display Current Weather Metrics
            st.metric(label="🌡 Temperature", value=f"{weather_info.get('temperature', 'N/A')}°C")
            st.metric(label="💨 Wind Speed", value=f"{weather_info.get('wind_speed', 'N/A')} m/s")
            st.metric(label="💧 Humidity", value=f"{weather_info.get('humidity', 'N/A')}%")
            st.metric(label="🌍 Pressure", value=f"{weather_info.get('pressure', 'N/A')} hPa")

            # 🌍 Interactive Map
            if "latitude" in weather_info and "longitude" in weather_info:
                lat, lon = weather_info["latitude"], weather_info["longitude"]
                st.subheader("🌍 Location Map")

                # Create folium map
                map = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")

                # Add marker for the city
                folium.Marker(
                    [lat, lon],
                    popup=f"{city_name} Weather",
                    icon=folium.Icon(color="red", icon="cloud")
                ).add_to(map)

                # Display the folium map
                folium_static(map)

            # 🌊 Retrieve Historical Weather Data for the Entered City
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                query = "SELECT date, temperature, humidity, wind_speed FROM weather_data WHERE city = %s"
                cursor.execute(query, (city_name,))
                rows = cursor.fetchall()

                if rows:
                    df = pd.DataFrame(rows, columns=["date", "temperature", "humidity", "wind_speed"])
                    st.subheader(f"📊 {city_name} Historical Weather Data")
                    st.dataframe(df)

                    # 📈 Temperature Trend (Line Graph)
                    st.subheader(f"📈 Temperature Trend in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(df["date"], df["temperature"], marker="o", linestyle="-", color="b", label="Temperature (°C)")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Temperature (°C)")
                    ax.set_title(f"📈 {city_name} Temperature Trend")
                    ax.legend()
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                    # 💧 Humidity Levels (Line Graph)
                    st.subheader(f"💧 Humidity Levels in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(df["date"], df["humidity"], marker="o", linestyle="-", color="g", label="Humidity (%)")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Humidity (%)")
                    ax.set_title(f"💧 {city_name} Humidity Levels")
                    ax.legend()
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                    # 🌬️ Wind Speed (Line Graph)
                    st.subheader(f"🌬️ Wind Speed in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(df["date"], df["wind_speed"], marker="o", linestyle="-", color="r", label="Wind Speed (m/s)")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Wind Speed (m/s)")
                    ax.set_title(f"🌬️ {city_name} Wind Speed Trends")
                    ax.legend()
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

                    # 📊 Bar Graph for Weather Metrics
                    st.subheader(f"📊 Weather Metrics Comparison in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    width = 0.3  # Width of the bars
                    x = np.arange(len(df["date"]))  # X-axis positions

                    ax.bar(x - width, df["temperature"], width=width, color="b", label="Temperature (°C)")
                    ax.bar(x, df["humidity"], width=width, color="g", label="Humidity (%)")
                    ax.bar(x + width, df["wind_speed"], width=width, color="r", label="Wind Speed (m/s)")

                    ax.set_xticks(x)
                    ax.set_xticklabels(df["date"], rotation=45)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Values")
                    ax.set_title(f"📊 {city_name} Weather Metrics Comparison")
                    ax.legend()
                    st.pyplot(fig)

                    # 📊 Histogram for Temperature Distribution
                    st.subheader(f"📊 Temperature Distribution in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.histplot(df["temperature"], bins=10, kde=True, color="b", ax=ax)
                    ax.set_xlabel("Temperature (°C)")
                    ax.set_ylabel("Frequency")
                    ax.set_title(f"📊 Temperature Distribution in {city_name}")
                    st.pyplot(fig)

                    # 📊 Histogram for Humidity Distribution
                    st.subheader(f"📊 Humidity Distribution in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.histplot(df["humidity"], bins=10, kde=True, color="g", ax=ax)
                    ax.set_xlabel("Humidity (%)")
                    ax.set_ylabel("Frequency")
                    ax.set_title(f"📊 Humidity Distribution in {city_name}")
                    st.pyplot(fig)

                    # 📊 Histogram for Wind Speed Distribution
                    st.subheader(f"📊 Wind Speed Distribution in {city_name}")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.histplot(df["wind_speed"], bins=10, kde=True, color="r", ax=ax)
                    ax.set_xlabel("Wind Speed (m/s)")
                    ax.set_ylabel("Frequency")
                    ax.set_title(f"📊 Wind Speed Distribution in {city_name}")
                    st.pyplot(fig)

                else:
                    st.warning(f"⚠️ No historical data found for {city_name}. Fetch weather first!")

            except mysql.connector.Error as err:
                st.error(f"❌ Database Error: {err}")

            finally:
                cursor.close()
                conn.close()

