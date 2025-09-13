## Overview
This module creates and html map and saves it to a given directory, using 4 parameters: year, latitude, longitude, path. The result is a map with 3 markers, which are closest filming sites to a given coordinate(longitude,latitude), filmed in a given year. The map is saved to path.
Librsaries used: argparse, re, geopy, math, time, folium.

## Algorithm
Parcing() reads input from user using argparse library. It saves 4 variables(year, latitude, longitude , path) in args and returns it. 

Read_data(path) takes path to a 'locations_list' file and reads it, it cleans missing data and saves dataset as a tuple of unique tuples, where each tuple looks like: (movie_name, year, address), example: ('One Night the Moon', '2001', 'South Australia, Australia').

Read_data uses another function format_line(line), is used to transform strings from "locations_list" to tuples. Format_line gets rid of all the unnecessary braces and brackets. A few ifs where added to read a movie called "(((Resonancia))) and "(Des)Encontros", which brake the main if.

name_to_coordinates(movie_set) function takes a tuple of tuples returned by read_data, replaces and address with coordinates, adds distance to an input coordinate, calculated by haversine(), to each tuple and filters them by years.

sort_by_distance(coordinate_list) takes a list from name_to_coordinate and returns 3 closest points to an input coordinate.

create_map, save_map and add_markers are simple and obvious functions, which use folium library.

The function also counts it's running time and shuts after 3 minutes.

## Usage
```python
main.py year latitude longitude path_to_locations_list 
```
## Output example
![alt text](https://github.com/BipolarPotato69/lab1-task2/blob/main/mappic.png?raw=true)
