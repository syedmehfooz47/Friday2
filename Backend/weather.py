# -*- coding: utf-8 -*-
"""
Weather Tool - Provides real-time weather information
Uses wttr.in API for weather data
"""

import requests
from typing import Dict, Any
from .logger import Logger


class WeatherTool:
    """Handle weather information queries"""
    
    def __init__(self):
        self.base_url = "https://wttr.in"
        Logger.log("WeatherTool initialized", "WEATHER")
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """
        Fetch weather information for a city
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather information
        """
        Logger.log(f"Fetching weather for: {city}", "WEATHER")
        
        if not city or not city.strip():
            return {"status": "error", "message": "City name is required"}
        
        try:
            url = f"{self.base_url}/{city}?format=j1"
            Logger.log(f"Making request to: {url}", "WEATHER")
            
            response = requests.get
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data['current_condition'][0]
            
            weather_info = {
                "status": "success",
                "city": city,
                "temperature_c": current['temp_C'],
                "temperature_f": current['temp_F'],
                "condition": current['weatherDesc'][0]['value'],
                "feels_like_c": current['FeelsLikeC'],
                "feels_like_f": current['FeelsLikeF'],
                "humidity": current['humidity'],
                "wind_speed_kmph": current['windspeedKmph'],
                "wind_speed_mph": current['windspeedMiles'],
                "pressure_mb": current['pressure'],
                "visibility_km": current['visibility'],
                "uv_index": current['uvIndex'],
                "precipitation_mm": current['precipMM']
            }
            
            Logger.log(f"Weather fetched successfully for {city}", "WEATHER")
            return weather_info
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timed out while fetching weather for {city}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch weather for {city}: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}
        except (KeyError, IndexError) as e:
            error_msg = f"Error parsing weather data for {city}: {str(e)}"
            Logger.log(error_msg, "ERROR")
            return {"status": "error", "message": error_msg}