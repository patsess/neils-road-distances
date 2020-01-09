
import logging
from pathlib import Path
import time
import urllib.request
import json
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)


UNIVERSITY_LOCATIONS_DICT = {
    'city': (51.5280, -0.1025),
    'exeter': (50.7365, -3.5344),
    'warick': (52.3793, -1.5615),
}


def get_road_distance(coords1, coords2, bing_maps_key):
    """Get road distance between two locations of latitude and longitude

    :param coords1: (float, float) tuple of lat, long for location 1
    :param coords2: (float, float) tuple of lat, long for location 2
    :param bing_maps_key: (str) developer key
    :return road_distance: (float) road distance
    """
    route_url = (
        "http://dev.virtualearth.net/REST/V1/Routes/Driving?"
        "wp.0={},{}&wp.1={},{}&key={}"
            .format(coords1[0], coords1[1], coords2[0], coords2[1],
                    bing_maps_key))

    logging.info('requesting url {}'.format(route_url))
    request = urllib.request.Request(route_url)
    response = urllib.request.urlopen(request)

    logging.info('decoding response from url')
    route_result = response.read().decode(encoding="utf-8")
    route_result = json.loads(route_result)

    null_list = [{'NA': 'NA'}]
    road_distance = (
        route_result.get("resourceSets", null_list)[0].get(
            "resources", null_list)[0].get("travelDistance", np.nan))
    logging.info('road distance: {}'.format(road_distance))
    return road_distance


def get_ane_distances_df():
    """Get data frame of A and E locations and other information

    :return df: (pd.DataFrame)
    """
    logging.info('getting A and E location data')
    df = pd.read_csv(Path(__file__).parents[1] / 'ane_locations.csv')
    return df


def add_ane_road_distances_to_df(bing_maps_key):
    """Add distances between A and E locations and universities

    :param bing_maps_key: (str) developer key
    :return df: (pd.DataFrame)
    """
    def _get_dist(ane_coords_, uni_coords_):
        road_distance_ = get_road_distance(
            coords1=uni_coords_, coords2=ane_coords_,
            bing_maps_key=bing_maps_key)
        time.sleep(2)  # avoid hitting api quickly
        return road_distance_

    df = get_ane_distances_df()
    for uni, uni_coords in UNIVERSITY_LOCATIONS_DICT.items():
        logging.info('getting road distances between A and E locations and {} '
                     'university'.format(uni))
        df['road_distance_{}'.format(uni)] = df.apply(
            lambda x: _get_dist((x['latitude'], x['longitude']),
                                uni_coords_=uni_coords), axis=1)

    return df


if __name__ == '__main__':
    bing_maps_key = (
        "AhtYO2E66CUyY2BZ08rpx2bWAR_Aa7xegAkw8CZbpOjmDFReYxkoBkwDR7Npj5_A")
    # road_distance = get_road_distance(
    #     coords1=(50.74, -3.53), coords2=(51.53, 0.10),
    #     bing_maps_key=bing_maps_key)
    # print(road_distance)

    df = add_ane_road_distances_to_df(bing_maps_key=bing_maps_key)
    df.to_csv('ane_road_distances.csv', index=False)
    print(df.head())
