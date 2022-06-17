import webbrowser
from matplotlib import axes
from matplotlib.transforms import Transform

import matplotlib.pyplot as plt
import folium

ax = axes.Axes

def plot_destination(coordinates: list, text: str, shape = 'r.', is_fanet = False):
    if is_fanet:
        plt.plot(coordinates[0], coordinates[1], shape, zorder=5, transform=ccrs.PlateCarree(), markersize=2)
    else:
        plt.plot(coordinates[0], coordinates[1], shape, zorder=5, transform=ccrs.PlateCarree(), markersize=5)
    plt.text(coordinates[0] + 0.001, coordinates[1], text, fontsize='medium', transform=ccrs.PlateCarree())

def main():
    
    origin = [50, 10]
    scenario_one = [50.01,10.01]
    map = folium.Map(origin, tiles='OpenStreetMap', zoom_start=15)
    folium.Marker(location=[origin[0],origin[1]],popup='Origin').add_to(map)
    folium.Marker(location=[scenario_one[0],scenario_one[1]],popup='Scenario 1').add_to(map)
    map.save("map.html")
    webbrowser.open("map.html")

if __name__ == '__main__':
    main()