"""
This module contains functions for reading and organizing the data
from a data set. It takes 4 values as an input: year, longitude, latitude, path.
It creates an html map that shows 3 markers, each showing a closest filming site. 
"""
import argparse
import re
import geopy
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
import time
import folium


def parcing():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type = str)
    parser.add_argument("latitude", type = float)
    parser.add_argument("longitude", type = float)
    parser.add_argument("path", type = str)
    args = parser.parse_args()
    return args 


def read_data(path):
    """
    This funtion takes a path to a dataset and returns a tuple of such tuples:
    (name of the film, year, address). The function igores all the damaged data(with "�")
    Example:
    read_data("locations_list")[:3]
    (('One Night the Moon', '2001', 'South Australia, Australia'), ('Project Peshawar', '2017', 'Amsterdam, Netherlands'), ('Bill Coors: The Will to Live', '2017', 'Colorado, USA'))
    """
    data = []
    with open(path, "r") as file:
        while True:
            line = file.readline()
            if line == "":
                return tuple(set(data))
            else:
                try:
                    if not "�" in line:
                        data.append(format_line(line))
                except IndexError:
                    continue


def format_line(line):
    """
    This function takes a string "Name (year)   address" and converts it to a tuple ("Name", "year", "address")
    >>> format_line('"(Des)Encontros" (2014) Canal 3, Santos, SP, Brazil')
    ('(Des)Encontros', '2014', '"Encontros"  Canal 3, Santos, SP, Brazil')
    """
    if line.startswith("((("): #for a film called (((Resonancia)))
        line = line[3:]
        line.replace(")))", "")
    elif line.startswith("("): #for films (Des)Encontros, (S)avis... 
        line = line.split()[0][1:-1]
    if line[1] != "(":
        line = re.sub(r"\{[^()]*\}", "",line)
        line_tuple = (line.split("(")[0].replace('"', "").strip(), line.split("(")[1][:4], re.sub(r"\([^()]*\)", "",line).strip().split("\t")[-1].replace("\n",""))
    else:
        line = re.sub(r"\{[^()]*\}", "",line)
        line_tuple = (line[1:].split('"')[0], line[1:].split('"')[1][2:6], re.sub(r"\([^()]*\)", "",line).strip().split("\t")[-1].replace("\n",""))
    return line_tuple


def name_to_coordinates(movie_set):
    """
    This function takes a tuple of tuples ((name, year, address), ...)
    transforms it to list of lists and adds coordinate and distance to lists [[name, year, coordinates, distance], ...]
    name_to_coordinates(read_data("locations_list")[:3])
    >>> name_to_coordinates((('Himaang', '2017', 'Katra, Jammu and Kashmir, India'), ('Kattu Puli', '2012', 'Filmistan Studios, Mumbai, Maharashtra, India'), ('The Call of the Heart', '1914', 'Long Beach, California, USA'), ('Watch', '2012', 'Seattle, Washington, USA'), ('The Wonderful World of Disney', '1995', 'Queensland, Australia')))
    [['Kattu Puli', '2012', (19.1653211, 72.84477306829942), 18519.670053828333], ['Watch', '2012', (47.6038321, -122.3300624), 753.5992998447974]]
    """
    new_movie_set = []
    try:
        for movie in movie_set:
            if time.perf_counter() - tic < 180:
                try:
                    if movie[1] == args.year:
                        movie = list(movie)
                        movie[-1] = (Nominatim(user_agent='tutorial').geocode(movie[-1], timeout=180).latitude, Nominatim(user_agent='tutorial').geocode(movie[-1], timeout=180).longitude)
                        movie.append(haversine(movie[-1], coordinate))
                        new_movie_set.append(movie)
                except AttributeError:
                    try:
                        if movie[1] == args.year:
                            movie[-1] = (Nominatim(user_agent='tutorial').geocode(",".join(movie[-1].split(",")[1:]), timeout=180).latitude, Nominatim(user_agent='tutorial').geocode(movie[-1].split(",")[1:], timeout=180).longitude)
                            movie.append(haversine(movie[-1], coordinate))
                            new_movie_set.append(movie)
                    except AttributeError:
                        return new_movie_set
            else:
                return new_movie_set
    except geopy.exc.GeocoderTimedOut:
        return new_movie_set
    return new_movie_set


def haversine(coordinate1,coordinate2):
    """
    Takes two tuples with coordinates and calculates the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    >>> haversine((34.1313, 56.34313),(12.34513, 45.12344))
    1961.9260400640153
    """
    lon1, lat1 = coordinate1
    lon2, lat2 = coordinate2
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def sort_by_distance(coordinate_list):
    """
    Function takes a list of lists (name, year, address, coordinates), sorts it
    by distance to a given coordinate and returns a list of 3 closest coordinates.
    >>> sort_by_distance([['Himaang', '2012', (32.9924858, 74.9318127), 18461.35306966315], ['Kattu Puli', '2012', (19.1653211, 72.84477306829942), 18519.670053828333], ['Watch', '2012', (47.6038321, -122.3300624), 753.5992998447974]])
    [['Watch', '2012', (47.6038321, -122.3300624), 753.5992998447974], ['Himaang', '2012', (32.9924858, 74.9318127), 18461.35306966315], ['Kattu Puli', '2012', (19.1653211, 72.84477306829942), 18519.670053828333]]
    """
    coordinate_list.sort(key = lambda x: x[-1])
    return coordinate_list[:3]


def create_map():
    """
    Function returns a folium map object.
    """
    my_map = folium.Map(location=[args.latitude, args.longitude], zoom_start=5, control_scale=True)
    return my_map


def save_map(name, path):
    """
    function saves a folium map with name and saves it to a given path in html format.
    """
    name.save(path)


def add_markers(map_name, coordinate_list):
    """
    functions adds markers of closest filming sites to a given folium map.
    """
    folium.LayerControl().add_to(map_name)
    folium.LayerControl().add_to(map_name)
    folium.LayerControl().add_to(map_name)
    folium.Marker(location = coordinate, popup = "Starting Point", tooltip='click', icon=folium.Icon(color='red',icon='none')).add_to(map_name)
    for movie in coordinate_list:
        folium.Marker(location = movie[2], popup = movie[0], tooltip='click').add_to(map_name)


args = parcing()
coordinate = (int(args.latitude), int(args.longitude))
tic = time.perf_counter()
movie_list =  sort_by_distance(name_to_coordinates(read_data(args.path)))
my_map = create_map()
add_markers(my_map, movie_list)
save_map(my_map, '/Users/timcook/Desktop/python/lab2.1/map.html')
