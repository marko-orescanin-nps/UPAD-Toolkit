from src.audio_fetch import AudioFetcher
from utils.geo_utils import get_circle_circum_locs
from utils.time_utils import utc_to_nanos, nanos_to_ymd_str
from src.constants import SENSOR_LAT, SENSOR_LON
import pandas as pd
import numpy as np
import ast
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

import argparse as ap

wav_dir = '/data/kraken/teams/acoustic_data/ais_data_labeling/wav/harp/'
wav_fmt = 'harp'
sr = 4000

detect = 10
buffer = 0

def plot_tracks(lats, lons):
    x_low  = SENSOR_LON + 1.0 # right hand side of plot 
    y_low  = SENSOR_LAT - .5

    x_high = SENSOR_LON - 1.0
    y_high = SENSOR_LAT + .5
    m = Basemap(
                projection='mill', 
                llcrnrlat = y_low,
                urcrnrlat = y_high,
                llcrnrlon = x_high,
                urcrnrlon = x_low,
                resolution = 'h'
                )
    m.drawmapboundary()
    m.fillcontinents(color='green', lake_color='aqua')
    m.drawcoastlines()

    m.plot(SENSOR_LAT, SENSOR_LON, marker='o', markerfacecolor='green', markeredgecolor='red', markersize=2.0)

    # draw detect zone
    detect_zone_x, detect_zone_y = get_circle_circum_locs(SENSOR_LAT, SENSOR_LON, detect)
    m.plot(detect_zone_x, detect_zone_y, latlon=True, color='black', linewidth=0.5, linestyle='--')

    # draw buffer zone
    detect_zone_x, detect_zone_y = get_circle_circum_locs(SENSOR_LAT, SENSOR_LON, detect+buffer)
    m.plot(detect_zone_x, detect_zone_y, latlon=True, color='black', linewidth=0.5, linestyle='--')

    m.plot(lons, lats, latlon=True, label='Ship Track', linewidth=1, linestyle='', marker='.', markersize=0.5)
    plt.show()

def check_isolated_trips(df_main, df_trip):
    res = []
    for i, row in df_trip.iterrows():
        exit_check = df_main[(df_main['ZONE_ENTER'] < row['ZONE_EXIT'])  & (row['ZONE_EXIT'] < df_main['ZONE_EXIT'])]
        enter_check = df_main[(df_main['ZONE_ENTER'] < row['ZONE_ENTER']) & (row['ZONE_ENTER'] < df_main['ZONE_EXIT'])]
        print(len(exit_check), len(enter_check))
        if len(exit_check) == 0 and len(enter_check) == 0:
            print(row['MMSI'], i)
            res.append(row)
    return res
    

def get_tracks(mmsi, audio_start_nanos, audio_end_nanos):
    df_tracks = pd.read_csv('/data/kraken/teams/acoustic_data/ais_data_labeling/ais_data/MarineCadastre_0/2021-08.csv')
    df_tracks = df_tracks.query(f'MMSI == {mmsi}')
    df_tracks['TIME_NANOS'] = df_tracks['BaseDateTime'].apply(utc_to_nanos)
    df_tracks = df_tracks.query(f'TIME_NANOS >= {audio_start_nanos}')
    df_tracks = df_tracks.query(f'TIME_NANOS <= {audio_end_nanos}')
    df_tracks = df_tracks[['TIME_NANOS', 'LAT', 'LON', 'SOG']]
    df_tracks.to_csv(f'/thumper/users/kraken/ais_data_labeling/class_samples/{detect}_{buffer}/A/tracks.csv', index=False)



if __name__ == '__main__':
    parser = ap.ArgumentParser()

    parser.add_argument('--sample_file',
                        type=str,
                        required=True)
    args = parser.parse_args()
    sample_file = args.sample_file

    df = pd.read_csv(sample_file).sort_values('ZONE_ENTER')
    df['START_YMD'] = df['ZONE_ENTER'].apply(nanos_to_ymd_str)
    df['END_YMD'] = df['ZONE_EXIT'].apply(nanos_to_ymd_str)

    df_trip = df.loc[df['CLASS'] == 'Class A']
    isolated_trips = check_isolated_trips(df, df_trip)

    # TODO: get isolated trips in list and plot out their courses 
    for trip in isolated_trips:
        msg_info = ast.literal_eval(trip['MSG_INFO'])
        # print(type(msg_info))
        lats = [pt[1] for pt in msg_info]
        lons = [pt[2] for pt in msg_info]
        print(lats)
        print(lons)
        plot_tracks(lats, lons)
        break
    # TODO: get MMSI, START_NANOS, END_NANOS, AUDIO_START_NANOS, AUDIO_END_NANOS, DESC

    # TODO: get audio and save to wav file

    # TODO: create INFO.md file for segment

    # TODO: create tracks.csv file for segment

    # TODO: create query to get associated tfrecords