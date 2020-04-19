from flask import Blueprint, jsonify
from functools import reduce
from haversine import haversine
import json
import pymongo
from app.models import Route

walk = Blueprint('walk', __name__)

'''
Due to the limitation Mongodb Atlas provide for advance operation, I am forced to manually 
combine the data myself
'''
# TODO: Research if Apache Spark can help simplifying helper operation


def round_point(point, decimal=2):
    return {'lat': round(point['lat'], decimal), 'lng': round(point['lng'], decimal)}


def map_route_location(route):
    return list(map(round_point, route["points"]))


def combine_points(points, route_points):
    for point in route_points:
        if point not in points:
            points.append(point)
    return points


def reduce_points_only(routes):
    points_only = map(map_route_location, routes)
    return reduce(combine_points, points_only)


def get_start_location(route):
    coordinates = route['starting_location']['coordinates']
    return (coordinates[1], coordinates[0])


def get_end_location(route):
    last_point = route['points'][-1]
    return (last_point['lat'], last_point['lng'])


# TODO: Figure out better way to handle many points on the client side
def manually_skip_points(points, number=20):
    '''
    To avoid returning too many points to the frontend, 
    for now I manually select every 20th points among all the points
    '''
    result = []
    for i, v in enumerate(points):
        if i % number == 0:
            result.append(v)
    return result


def map_points_city_distance(document):
    return {
        'points': manually_skip_points(document['points']),
        'city': document['city'],
        'distance': haversine(get_start_location(document), get_end_location(document))
    }


'''
For now I can preload the route data from database to increase the reading speed
No need to worry about consistent issue for now since there is only one client using the data
'''
# TODO: Use Redis to cache the data
all_routes_preload = list(
    map(map_points_city_distance, Route.get_all_routes()))

points_only = list(reduce_points_only(all_routes_preload))


@walk.route('/')
def index():
    return jsonify(all_routes_preload)


@walk.route('/all_points')
def get_heat_map():
    return jsonify(points_only)


@walk.route('/top_routes')
# TODO: optional parmeter to control limit of paths
def get_top_routes():
    # For now return top 5 of the longest paths
    return jsonify(sorted(all_routes_preload, reverse=True, key=lambda route: route['distance'])[0:5])

# TODO: Use Scikit-learn's kx mean algorithm to cluster out all poitns
# TODO: Use Convex hull algorithm to draw out the boundray
# Look into Scipy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html
@walk.route('/regions/kxmean/<groups>')
def kxmean(groups):
    return jsonify(groups)
