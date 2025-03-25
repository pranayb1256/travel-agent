import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WEATHER_API_KEY = "b4093efa0fd4431d894b85d9de084953"
print(WEATHER_API_KEY)
def get_weather_info(destination):
    """
    Fetches real-time weather data for a given destination using OpenWeatherMap API.
    """
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(weather_url)
        data = response.json()
        
        # Debugging: Print API response to check errors
        print("API Response:", data)

        # Check if the request was successful
        if response.status_code != 200 or "main" not in data:
            return f"❌ Weather data not available: {data.get('message', 'Unknown error')}"
        
        # Extract weather details
        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return f"🌡️ Temperature: {temp}°C\n💨 Wind Speed: {wind_speed} m/s\n💧 Humidity: {humidity}%\n☁️ Condition: {weather_desc}"
    
    except requests.exceptions.RequestException as e:
        return f"❌ API Request Failed: {e}"

if __name__ == "__main__":
    city = input("Enter a city name: ")
    weather_info = get_weather_info(city)
    print(weather_info)