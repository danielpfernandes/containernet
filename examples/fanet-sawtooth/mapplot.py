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
    expected_scenario_one = get_coordinates(coordinates[1])
    expected_scenario_two = get_coordinates(coordinates[2])
    actual_scenario_three = get_coordinates(coordinates[3])
    actual_scenario_four = get_coordinates(coordinates[4])
    actual_scenario_five = get_coordinates(coordinates[5])
    mission_coordinates = [origin,expected_scenario_one,expected_scenario_two]
    actual_coordinates = [expected_scenario_two, actual_scenario_three, actual_scenario_four, actual_scenario_five]
    expected_names = ['Origin', 'Scenario 1', 'Scenarios 2,3,4,5']
    actual_names = ['Scenario 2','Scenario 3', 'Scenario 4', 'Scenario 5']
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