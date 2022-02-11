import argparse
import re
from turtle import color
import geopy
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
import time
import folium


#Parcing
parser = argparse.ArgumentParser()
parser.add_argument("year", type = str)
parser.add_argument("latitude", type = float)
parser.add_argument("longitude", type = float)
parser.add_argument("path", type = str)
args = parser.parse_args()

coordinate = (int(args.latitude), int(args.longitude))
tic = time.perf_counter()


def read_data(path):
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
    if line.startswith("((("): #for a film called (((Resonancia)))
        line = line[3:]
        line.replace(")))", "")
    elif line.startswith("("):
        line = line.split()[0][1:-1]
    if line[1] != "(":
        line_tuple = (line.split("(")[0].replace('"', "").strip(), line.split("(")[1][:4], re.sub(r"\([^()]*\)", "",line).strip().split("\t")[-1].replace("\n",""))
    else:
        line_tuple = (line[1:].split('"')[0], line[1:].split('"')[1][2:6], re.sub(r"\([^()]*\)", "",line).strip().split("\t")[-1].replace("\n",""))
    return line_tuple


def name_to_coordinates(movie_set):
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
                        print("+")
                except AttributeError:
                    try:
                        if movie[1] == args.year:
                            movie[-1] = (Nominatim(user_agent='tutorial').geocode(",".join(movie[-1].split(",")[1:]), timeout=180).latitude, Nominatim(user_agent='tutorial').geocode(movie[-1].split(",")[1:], timeout=180).longitude)
                            movie.append(haversine(movie[-1], coordinate))
                            new_movie_set.append(movie)
                            print("-")
                    except AttributeError:
                        return new_movie_set
            else:
                return new_movie_set
    except geopy.exc.GeocoderTimedOut:
        return new_movie_set


def haversine(coordinate1,coordinate2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
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
    coordinate_list.sort(key = lambda x: x[-1])
    return coordinate_list[:3]


def create_map():
    my_map = folium.Map(location=[args.latitude, args.longitude], zoom_start=5, control_scale=True)
    return my_map


def save_map(name, path):
    name.save(path)


def add_markers(map_name, coordinate_list):
    folium.Marker(location = coordinate, popup = "Starting Point", tooltip='click', icon=folium.Icon(color='red',icon='none')).add_to(map_name)
    for movie in coordinate_list:
        folium.Marker(location = movie[2], popup = movie[0], tooltip='click').add_to(map_name)


movie_list =  sort_by_distance(name_to_coordinates(read_data(args.path)))
my_map = create_map()
add_markers(my_map, movie_list)
save_map(my_map, '/Users/timcook/Desktop/python/lab2.1/map.html')
