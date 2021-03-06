import os
import json
from flask import Flask, render_template, request
import requests

# Load the Azure Maps key from the .env file
MAP_KEY = "F6N4grXV8He3RimiYXHB6ztl3kek-kCn7ocuDjVzvAM"

# Load the WAQI
WAQI_API_KEY = "862e50d3dc7249b66edbae155621152d005833c8"
WAQI_API_URL = "https://api.waqi.info/map/bounds/?latlng={},{},{},{}&token={}"
WAQI_API_BASE_URL = "https://api.waqi.info/feed/here/?token={}"
WEATHER_URL = "http://api.weatherapi.com/v1/current.json?key=30e5923990c74026815164016200112&q={}"

# Initialize the Flask app
app = Flask(__name__)

# Handle requests to the root of the web site, returning the home page


@app.route("/")
def home():
    # Create data for the home page to pass the maps key
    data = {"map_key": MAP_KEY}
    # Return the rendered HTML page
    return render_template("home.html", data=data)


def get_color(aqi):
    # Convert the AQI value to a color
    if aqi <= 50:
        return "#009966"
    if aqi <= 100:
        return "#ffde33"
    if aqi <= 150:
        return "#ff9933"
    if aqi <= 200:
        return "#cc0033"
    if aqi <= 300:
        return "#660099"
    return "#7e0023"


def load_aqi_data(lon1, lat1, lon2, lat2):
    # Load the air quality data
    url = WAQI_API_URL.format(lat1, lon1, lat2, lon2, WAQI_API_KEY)
    aqi_data = requests.get(url)

    # Create a GeoJSON feature collection from the data
    feature_collection = {
        "type": "FeatureCollection",
        "features": []
    }

    for value in aqi_data.json()["data"]:
        # Filter out empty values
        if value["aqi"] != "-":
            feature_collection["features"].append({
                "type": "Feature",
                "aqi": value["aqi"],
                "properties": {
                    "color": get_color(int(value["aqi"])),
                    "aqi": value["aqi"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [value['lon'], value['lat']]
                }
            })

    return feature_collection


@app.route("/aqi", methods=["GET"])
def get_aqi():
    # Get the bounds from the request
    bounds = request.args["bounds"].split(",")

    # Load the AQI data and create the GeoJSON for the given bounds
    return json.dumps(load_aqi_data(bounds[0], bounds[1], bounds[2], bounds[3]))


@app.route("/here", methods=["GET"])
def get_aqi_here():
    # Load the air quality data in the current location
    url = WAQI_API_BASE_URL.format(WAQI_API_KEY)
    aqi_data_here = requests.get(url)

    return aqi_data_here.json()


@app.route("/weather", methods=["GET"])
def get_weather_here():
    search = request.args["search"]
    url = WEATHER_URL.format(search)
    weather_data = requests.get(url)

    return weather_data.json()
