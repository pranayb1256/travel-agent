import os
from textwrap import dedent
import openai
import streamlit as st
import folium
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from streamlit_folium import folium_static
import requests
from fpdf import FPDF
from geopy.geocoders import Nominatim
import dotenv

dotenv.load_dotenv(override=True)
OPENAI_API_KEY =os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
AVIATION_API_KEY = os.getenv("AVIATION_API_KEY")

if not OPENAI_API_KEY or not SERP_API_KEY or not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("Missing API Keys! Please add them.")
    st.stop()

client = openai.OpenAI()

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("🌍 AI Travel Planner")
st.caption("Plan your next adventure with AI-powered research and itinerary generation.")

destination = st.text_input("📍 Where do you want to go?")
num_days = st.number_input("📅 How many days?", min_value=1, max_value=30, value=5)
budget = st.selectbox("💰 Choose Budget Level", ["Low", "Mid", "Luxury"])
get_weather = st.checkbox("🌦️ Include Weather Forecast")
get_cuisine = st.checkbox("🍽️ Include Local Cuisine Recommendations")
get_exchange_rate = st.checkbox("💱 Include Currency Exchange Rate")
get_transport = st.checkbox("🚕 Include Transport Info")
get_emergency_info = st.checkbox("🏥 Include Emergency Contacts")
get_accommodation = st.checkbox("🏨 Include Accommodation Suggestions")
get_shopping = st.checkbox("🛍️ Include Shopping & Souvenirs Guide")
get_packing_list = st.checkbox("🎒 Include Smart Packing List")
get_local_phrases = st.checkbox("🔊 Include Basic Local Phrases")
get_flight_info = st.checkbox("🛩️ Include Real-Time Flight Tracker")

import requests

def get_currency_exchange_rate(currency):
   
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
    
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("result") != "success":
            return f"API Error: {data.get('error-type', 'Unknown error')}"
        if "conversion_rates" not in data:
            return " Error: No conversion rates found in API response."
        return data["conversion_rates"].get(currency, "Currency Not Found.")
    except requests.exceptions.RequestException as e:
        return f" API Request Failed: {e}"


def get_transport_info(destination):
    prompt = f"Provide public transport and taxi options in {destination}."
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def get_emergency_info(destination):
    prompt = f"List emergency contacts (hospitals, embassies, police) in {destination}."
    return client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def get_accommodation(destination, budget):
    prompt = f"List best {budget}-budget hotels and stays in {destination}."
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def get_shopping_guide(destination):
    prompt = f"Provide famous shopping places and souvenirs in {destination}."
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def get_packing_list(destination, num_days):
    prompt = f"Generate a packing list for a {num_days}-day trip to {destination} considering weather and activities."
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content


def get_flight_info(flight_iata):
    if not AVIATION_API_KEY:
        return " Missing API Key for AviationStack."

    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATION_API_KEY}&flight_iata={flight_iata}"
    response = requests.get(url).json()
    
    if "data" in response and len(response["data"]) > 0:
        flight = response["data"][0]

        airline = flight.get("airline", {}).get("name", "Unknown Airline")
        status = flight.get("flight_status", "Unknown Status")

        departure_airport = flight.get("departure", {}).get("airport", "Unknown Airport")
        departure_time = flight.get("departure", {}).get("estimated", "N/A")

        arrival_airport = flight.get("arrival", {}).get("airport", "Unknown Airport")
        arrival_time = flight.get("arrival", {}).get("estimated", "N/A")

        return f"""
        ✈️ **Flight Status**: {status}
        🏢 **Airline**: {airline}
        🛫 **Departure**: {departure_airport} at {departure_time}
        🛬 **Arrival**: {arrival_airport} at {arrival_time}
        """
    
    return " Flight information not available. Please check the flight code."

def get_local_phrases(destination):
    prompt = f"Provide essential travel phrases in the local language of {destination}."
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    
def get_weather_info(destination):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(weather_url)
        data = response.json()
        if response.status_code != 200 or "main" not in data:
            return f" Weather data not available: {data.get('message', 'Unknown error')}"
        
        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return f"🌡️ **Temperature:** {temp}°C\n💨 **Wind Speed:** {wind_speed} m/s\n💧 **Humidity:** {humidity}%\n☁️ **Condition:** {weather_desc}"

    except requests.exceptions.RequestException as e:
        return f" API Request Failed: {e}"



if st.button("🛫 Generate Travel Plan"):
    if not destination.strip():
        st.warning("⚠️ Please enter a valid destination.")
    else:
        st.subheader("📌 AI-Powered Travel Research")
        st.markdown(f"Researching {destination} for {num_days} days...")
        
        if get_accommodation:
            st.subheader("🏨 Accommodation Suggestions")
            st.markdown(get_accommodation(destination, budget))
        
        if get_weather:
          st.subheader("🌦️ Real-Time Weather Forecast")
          st.markdown(get_weather_info(destination))
        
        if get_cuisine:
            st.subheader("🍽️ Local Cuisine")
            st.markdown("Cuisine Recommendations Here")
        
        if get_exchange_rate:
            st.subheader("💱 Currency Exchange")
            st.markdown(f"1 USD = {get_currency_exchange_rate('INR')} INR")
        
        if get_transport:
            st.subheader("🚕 Transport Options")
            st.markdown(get_transport_info(destination))
        
        if get_emergency_info:
            st.subheader("🏥 Emergency Contacts")
            st.markdown(get_emergency_info(destination))
        
        if get_shopping:
            st.subheader("🛍️ Shopping & Souvenirs Guide")
            st.markdown(get_shopping_guide(destination))
        
        if get_packing_list:
            st.subheader("🎒 Smart Packing List")
            st.markdown(get_packing_list(destination, num_days))
        
        if get_local_phrases:
            st.subheader("🔊 Basic Local Language Phrases")
            st.markdown(get_local_phrases(destination))
        
        if get_flight_info:
            st.subheader("🛩️ Real-Time Flight Tracker")
            flight_code = st.text_input("Enter Flight IATA Code (e.g., AI101)")
            st.markdown(get_flight_info(flight_code))
        st.subheader("🗺️ Interactive Map")
        
        map_center = Nominatim(user_agent="geoapi").geocode(destination)
        if map_center:
            m = folium.Map(location=[map_center.latitude, map_center.longitude], zoom_start=12)
            folium.Marker([map_center.latitude, map_center.longitude], tooltip=destination).add_to(m)
            folium_static(m)
        else:
            st.warning("Could not generate map for this location.")
