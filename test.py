import requests, json
import folium
from IPython.display import display


def style_function(color):
    return lambda feature: dict(color=color,
                              weight=3,
                              opacity=0.5)

# GET request
#response = requests.get("https://api.tomtom.com/routing/1/calculateRoute/52.50931,13.42936:52.50274,13.43872/json?key=bFhiFkO3kvbqhYxcYILAZdFTk5XZ7UgA")
response = requests.get("https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf624897815c04d1a74c7aa894deb24b7e0f41&start=8.681495,49.41461&end=8.687872,49.420318")

# Get the response in json to dict type
route = response.json()
#print(json.dumps(route, indent=4)) # Makes the json dict readable


#routePoints = route["routes"][0]["legs"][0]["points"]
m = folium.Map(location=[49.4, 8.68])
folium.Marker([49.41461, 8.681495], tooltip="Source").add_to(m)
folium.Marker([49.420318, 8.687872], tooltip="Destination", icon=folium.Icon(color="green")).add_to(m)


#for point in routePoints:
#    coord = [point["latitude"], point["longitude"]]
#    folium.Marker(coord, tooltip="Route").add_to(m)
folium.features.GeoJson(data=route, name='Route without construction sites', style_function=style_function('#FF0000'), overlay=True).add_to(m)
m.save("./templates/map.html")
