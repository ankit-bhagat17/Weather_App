import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from weather import get_weather

st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌦️ Weather Dashboard with Data Visualizations")

# Load state-city data
with open("data.json", "r") as f:
    state_city_data = json.load(f)

state = st.selectbox("📍 Select State", sorted(state_city_data.keys()))
city = st.selectbox("🏙️ Select City", state_city_data[state])

if st.button("🔍 Get Weather"):
    with st.spinner("Fetching weather..."):
        weather = get_weather(city, state)

    if weather:
        st.success(f"✅ Weather Data for {city}, {state}")

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temp (°C)", f"{weather['temperature']}")
        col2.metric("💧 Humidity (%)", f"{weather['humidity']}")
        col3.metric("🌬️ Wind Speed (m/s)", f"{weather['wind_speed']}")

        st.write(f"📅 Date/Time: {weather['date']}")
        st.write(f"🌥️ Condition: {weather['weather']}")

        # Map
        st.subheader("🗺️ Location Map")
        m = folium.Map(location=[weather['lat'], weather['lon']], zoom_start=10)
        folium.Marker([weather['lat'], weather['lon']], tooltip=weather['weather']).add_to(m)
        folium_static(m)

        # Simulated 7-day Data
        st.subheader("📊 Simulated 7-Day Weather Trends")
        df = pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=7),
            "Temperature": [weather["temperature"] + i for i in range(7)],
            "Humidity": [weather["humidity"] - i for i in range(7)],
            "Wind Speed": [weather["wind_speed"] + 0.2 * i for i in range(7)],
        })

        st.dataframe(df)

        # Option to download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="weather_simulated.csv", mime="text/csv")

        # Line Chart
        st.subheader("📈 Line Chart")
        fig1, ax1 = plt.subplots()
        df.plot(x="Date", y=["Temperature", "Humidity", "Wind Speed"], marker='o', ax=ax1)
        ax1.set_title("Weather Metrics Over Time")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Value")
        ax1.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        # Histogram
        st.subheader("📊 Temperature Distribution")
        fig2, ax2 = plt.subplots()
        sns.histplot(df["Temperature"], kde=True, color="skyblue", ax=ax2)
        ax2.set_title("Temperature Histogram")
        st.pyplot(fig2)

        # Bar Chart
        st.subheader("📉 Wind Speed Bar Chart")
        fig3, ax3 = plt.subplots()
        ax3.bar(df["Date"].dt.strftime('%b %d'), df["Wind Speed"], color="orange")
        ax3.set_title("Wind Speed Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

        # Correlation Heatmap
        st.subheader("🔥 Correlation Heatmap")
        fig4, ax4 = plt.subplots()
        sns.heatmap(df[["Temperature", "Humidity", "Wind Speed"]].corr(), annot=True, cmap="coolwarm", ax=ax4)
        ax4.set_title("Correlation Matrix")
        st.pyplot(fig4)

        # Box Plot
        st.subheader("📦 Metric Variability (Box Plot)")
        fig5, ax5 = plt.subplots()
        sns.boxplot(data=df[["Temperature", "Humidity", "Wind Speed"]], ax=ax5)
        ax5.set_title("Metric Spread Across 7 Days")
        st.pyplot(fig5)

    else:
        st.error("⚠️ Failed to get weather data. Check city/state name or API key.")

