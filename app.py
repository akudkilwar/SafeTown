from flask import Flask, render_template, request
from flask.helpers import url_for
from folium.features import ColorLine
from haversine import haversine, Unit
#To prevent injection attacks while returning something that's input from user.
from markupsafe import escape
import requests
import json
import folium
from IPython.display import display
from werkzeug.datastructures import FileStorage
from werkzeug.utils import redirect
import csv
import pandas as pd
import datetime
import severity

# Find in secrets.txt
ORS_API_KEY = "????"
TOMTOM_API_KEY = "????"

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/directions", methods=["GET", "POST"]) # GET is needed for just visiting the url. POST is for form data submission.
def directions():
    endTime = datetime.datetime.now()
    print(f"Time Before Reading Data = {endTime}")
    if request.method == "POST":
        # Get String input from form.
        src = request.form["src"]
        dst = request.form["dst"]

        # Edit the string to fit the api url.
        keywords = src.split()
        src = ""

        for word in keywords:
            src = src + word + "%20"

        keywords = dst.split()
        dst = ""

        for word in keywords:
            dst = dst + word + "%20"

        # ORS API call to 'Forward Geocode Service'
        geocode_api_url_src = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={src}"
        response = requests.get(geocode_api_url_src).json()
        srcCoords = [str(response["features"][0]["geometry"]["coordinates"][1]), str(response["features"][0]["geometry"]["coordinates"][0])]

        geocode_api_url_dst = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={dst}"
        response = requests.get(geocode_api_url_dst).json()
        dstCoords = [str(response["features"][0]["geometry"]["coordinates"][1]), str(response["features"][0]["geometry"]["coordinates"][0])]

        # TomTom API call to 'Directions Service (GET)'
        # USE THIS RESPONSE TO PRINT ROUTE STATISTICS LATER

        directions_api_url = f"https://api.tomtom.com/routing/1/calculateRoute/{srcCoords[0]},{srcCoords[1]}:{dstCoords[0]},{dstCoords[1]}/json?maxAlternatives=1&key={TOMTOM_API_KEY}"
        response = requests.get(directions_api_url).json()

        route1 = response["routes"][0]["legs"][0]["points"]
        route2 = response["routes"][1]["legs"][0]["points"]
        route1_dist = response["routes"][0]["summary"]["lengthInMeters"]
        route2_dist = response["routes"][1]["summary"]["lengthInMeters"]
        route1_time = response["routes"][0]["summary"]["travelTimeInSeconds"]
        route2_time = response["routes"][0]["summary"]["travelTimeInSeconds"]


        # Typecasting coordinates to float
        srcCoords[0] = float(srcCoords[0])
        srcCoords[1] = float(srcCoords[1])
        dstCoords[0] = float(dstCoords[0])
        dstCoords[1] = float(dstCoords[1])

        # Creating folium maps with source and destination markers.
        m = folium.Map(location=srcCoords)
        folium.Marker(srcCoords, tooltip="Source").add_to(m)
        folium.Marker(dstCoords, tooltip="Destination", icon=folium.Icon(color="green")).add_to(m)

        # Can make this a numpy array for more speed.
        # Points as list of tuples to feed folium polyLine
        pointsForRoute1 = []
        pointsForRoute2 = []
        severityCount1 = 0
        severityCount2 = 0

        for point in route1:
            pointsForRoute1.append((point["latitude"], point["longitude"]))

        for point in route2:
            pointsForRoute2.append((point["latitude"], point["longitude"]))


        df = pd.read_csv("Data/US_Accidents_Dec20_Updated.csv")

        selectedDf = df[df["State"] == "WI"]

        severityCount1, severityCount2 = severity.checkSeverity(selectedDf, pointsForRoute1, pointsForRoute2)


        # Add polyLines to folium map
        if severityCount1/route1_dist > severityCount2/route2_dist:
            folium.PolyLine(pointsForRoute2,color='orange',weight=15,opacity=0.8).add_to(m)
            print(f"Distance: {route2_dist} m")
            print(f"Time: {route2_time/60} minutes")
        else:
            folium.PolyLine(pointsForRoute1,color='yellow',weight=15,opacity=0.8).add_to(m)
            print(f"Distance: {route1_dist} m")
            print(f"Time: {route1_time/60} minutes")


        m.save("./templates/map.html")
        print(datetime.datetime.now()-endTime)

        return render_template("map.html")
    else:
        return render_template("directions.html")


def checkHaversineEquality(start, end, crashpoint, error=0.5):
    if abs(haversine(crashpoint, start, unit=Unit.KILOMETERS) + haversine(crashpoint, end, unit=Unit.KILOMETERS) - haversine(start, end)) <= error*(haversine(start, end, unit=Unit.KILOMETERS)):
        return True
    return False