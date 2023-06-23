import webbrowser, folium, csv, os

from pyexpat import features
from sys import prefix
from folium import plugins


def add_markers(map: folium.Map, list_of_coordinates: list, list_of_names: list, icon_color='blue'):
    i = 0
    for coordinate in list_of_coordinates:
        folium.Circle(location=[float(coordinate[0]), float(coordinate[1])],
            popup=list_of_names[i],
            color=icon_color,
            fill=True).add_to(map)
        i += 1

def get_coordinates_from_file() -> dict:
    coordinates = []
    with open(os.path.dirname(os.path.abspath(__file__)) + '/coordinates.csv') as csv_file:
        file = csv.DictReader(csv_file, delimiter=',')
        for row in file:
            coordinates.append(row)
    return coordinates

def get_coordinates(coordinates: dict) -> list:
    return [float(coordinates['latitude']), float (coordinates['longitude'])]

            
def main():
    
    coordinates = get_coordinates_from_file()
    origin= get_coordinates(coordinates[0])
    expected_stage_one = get_coordinates(coordinates[1])
    expected_stage_two = get_coordinates(coordinates[2])
    actual_stage_three = get_coordinates(coordinates[3])
    actual_stage_four = get_coordinates(coordinates[4])
    actual_stage_five = get_coordinates(coordinates[5])
    mission_coordinates = [origin,expected_stage_one,expected_stage_two]
    actual_coordinates = [expected_stage_two, actual_stage_three, actual_stage_four, actual_stage_five]
    expected_names = ['Origin', 'Stage 1A', 'Stages 2,3,4,5']
    actual_names = ['Stage 2A','Stage 3A', 'Stage 4A', 'Stage 5A']
    map = folium.Map(origin, tiles='OpenStreetMap', zoom_start=13)
    add_markers(map, mission_coordinates, expected_names)
    add_markers(map, actual_coordinates, actual_names, icon_color='red')
    folium.PolyLine(actual_coordinates, color='red').add_to(map)
    folium.PolyLine(mission_coordinates).add_to(map)
    minimap = plugins.MiniMap()
    map.add_child(minimap)
    map.save("map.html")
    webbrowser.open("map.html")

if __name__ == '__main__':
    main()