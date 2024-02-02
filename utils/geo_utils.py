import geopy.distance
from geographiclib.geodesic import Geodesic
from src.constants import *
from math import asin, atan2, cos, sin, pi


def get_bearing(lat1, lon1, lat2, lon2):
    '''
    Description: given a latitude and longitude, return the bearing from the sensor location

    :lat1: latitude to calculate bearing
    :lon1: longitude to calculate bearing
    :lat2: latitude of target to calculate bearing
    :lon2: longitude of target to calculate bearing

    :returns: bearing between supplied lat lon point and target lat lon point 
    '''
    return Geodesic.WGS84.Inverse(lat2, lon2, lat1, lon1)['azi1'] % 360

def get_range(lat1, lon1, lat2, lon2):
    '''
    Description: given a latitude and longitude, return the range from the sensor location

    :lat1: latitude to calculate range
    :lon1: longitude to calculate range
    :lat2: latitude of target to calculate range
    :lon2: longitude of target to calculate range

    :returns: distance between supplied lat lon point and target location
    '''
    distance = geopy.distance.geodesic(
        (lat2, lon2), 
        (lat1, lon1)
        ).km
    return distance # km
 
'''
Adapted from https://stochasticcoder.com/2016/04/06/python-custom-distance-radius-with-basemap/
'''
def get_circle_circum_locs(lat, lon, radius_km):
    '''
    Description: get points in circle around a given lat lon point at a distance

    :lat: latitude of center point
    :lon: longitude of center point
    :radius_km: radius of circle in kilometers

    :returns: two lists with lats and lons
    '''
    lats = []
    lons = []

    for brng in range(0,360):
        lat_c, lon_c = get_circum_loc(lat, lon, brng, radius_km)
        lats.append(lat_c)
        lons.append(lon_c)

    return lons, lats


def get_circum_loc(lat1, lon1, brng, distance_km):
    '''
    Description: given a latitude longitude, bearing, and distance, calculate the new latitude/longitude

    :lat1: latitude origin
    :lon1: longitude origin
    :brng: bearing
    :distance_km: distance in kilometers

    :returns: (lat, lon) of new position
    '''
    lat1 = lat1 * pi/ 180.0
    lon1 = lon1 * pi / 180.0
    #earth radius
    R = 6378.1 # km

    distance_km = distance_km/R

    brng = (brng / 90)* pi / 2

    lat2 = asin(sin(lat1) * cos(distance_km) 
    + cos(lat1) * sin(distance_km) * cos(brng))

    lon2 = lon1 + atan2(sin(brng)*sin(distance_km)
    * cos(lat1),cos(distance_km)-sin(lat1)*sin(lat2))

    lon2 = 180.0 * lon2/ pi
    lat2 = 180.0 * lat2/ pi

    return lat2, lon2