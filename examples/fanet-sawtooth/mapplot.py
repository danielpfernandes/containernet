from cartopy.io.img_tiles import OSM
from matplotlib import axes
from matplotlib.transforms import Transform

import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt


ax = axes.Axes

def plot_destination(coordinates: list[float], text: str, shape = 'r.', is_fanet = False):
    if is_fanet:
        plt.plot(coordinates[0], coordinates[1], shape, zorder=5, transform=ccrs.PlateCarree(), markersize=2)
    else:
        plt.plot(coordinates[0], coordinates[1], shape, zorder=5, transform=ccrs.PlateCarree(), markersize=5)
    plt.text(coordinates[0] + 0.001, coordinates[1], text, fontsize='medium', transform=ccrs.PlateCarree())

def main():
    cf.BORDERS
    cf.COASTLINE
    
    imagery = OSM()
    origin = [10, 50]
    scenario_one = [10.01,50.01]
    
    ax = plt.axes(projection=imagery.crs)
    ax.set_extent((origin[0] - 0.001, origin[0] + 0.025,
                   origin[1] - 0.001, origin[1] + 0.025))
    ax.add_image(imagery, 14)
    plot_destination(origin, 'FANET', shape='b.', is_fanet=True)
    plot_destination(scenario_one, 'Scenario 1')
    
    plt.show()

if __name__ == '__main__':
    main()