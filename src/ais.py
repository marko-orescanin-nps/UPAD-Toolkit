import tables
import pandas as pd
from utils.time_utils import greg_to_nanos, nanos_to_ymd_str, uscg_date_to_nanos, uscg_ais_to_nanos, marine_cadastre_to_nanos, utc_to_nanos
from utils.geo_utils import get_bearing, get_range 
from utils.mat_utils import fetch_all_mat_files, mmsi_info_from_mat
from utils.mmsi_scraper import mmsi_scraper
from src.constants import get_desig_class, SENSOR_LAT, SENSOR_LON

import time
import os
import tqdm

from src.constants import *

class Trips:
    def add_or_update_trip(self, df_trips, new_trip, mmsi, msg_time_nanos, ship_desig, rng, lat, lon, brg, spd):
        '''
        Description: updates trip dataframe with new trip information

        :df_trips:
        :new_trip:
        :mmsi:
        :msg_time_nanos:
        :ship_desig:
        :rng:
        :brg:
        :lat:
        :lon:
        :spd:

        :returns:
        '''
        if new_trip: # start of new trip
            row = pd.Series({
                'MMSI'      : mmsi,
                'ZONE_ENTER': msg_time_nanos,
                'ZONE_EXIT' : msg_time_nanos,
                'DESIG'     : ship_desig,
                'CPA'       : rng,
                'CPA_TIME'  : msg_time_nanos,
                'MSG_INFO'  : [(msg_time_nanos, lat, lon, brg, rng, spd)]
                })
            df_trips = pd.concat([df_trips, row.to_frame().T], ignore_index=True)
        else: # continuation of current trip
            # find current trip in df_trips
            current_trip_idx = df_trips[df_trips['MMSI']==mmsi].index[-1]
            if rng < df_trips.iloc[current_trip_idx, 4]: # new cpa
                df_trips.iloc[current_trip_idx, 4] = rng
                df_trips.iloc[current_trip_idx, 5] = msg_time_nanos
            df_trips.iloc[current_trip_idx, 2] = msg_time_nanos
            msg_info = (msg_time_nanos, lat, lon, brg, rng, spd)
            df_trips.iloc[current_trip_idx, 6].append(msg_info)

        return df_trips
    
    def time_filter_df_trips(self, df_trips, start_nanos, end_nanos):
        '''
        Description: Given a period of time get the dataframe of trips that satisfy that time period

        :df_trips: trip dataframe to filter
        :start_nanos: start of interval
        :end_nanos: end of interval
        
        :returns: filtered df_trips
        '''
        return df_trips[((df_trips["ZONE_ENTER"] <= start_nanos) & (start_nanos < df_trips["ZONE_EXIT"])) | ((df_trips["ZONE_ENTER"] <= end_nanos) & (end_nanos < df_trips["ZONE_EXIT"]))]
        

    
class Mars(Trips):
    def __init__(self, 
                user_start_nanos,
                user_end_nanos,
                detect_range, 
                buffer_range,
                ais_data,
                mmsi_meta_cache
                ):
        Trips.__init__(self)
        self.df_trips_detect, self.df_trips_buffer = self._get_trips(user_start_nanos,
                                                                          user_end_nanos,
                                                                          detect_range,
                                                                          buffer_range,
                                                                          ais_data,
                                                                          mmsi_meta_cache)
    def time_filter_df_trips(self, df_trips, start_nanos, end_nanos):
        '''
        Given a period of time get the dataframe of trips that satisfy that time period
        '''
        
        return df_trips[(df_trips['ZONE_ENTER'].between(start_nanos, end_nanos)) | \
                        (df_trips['ZONE_EXIT'].between(start_nanos, end_nanos)) | \
                        ((start_nanos >= df_trips['ZONE_ENTER']) & (start_nanos <= df_trips['ZONE_EXIT'])) | \
                        ((end_nanos >= df_trips['ZONE_ENTER']) & (end_nanos <= df_trips['ZONE_EXIT']))]

    def get_daily_tracks(self, mat_h5s, mmsi_tgt):
        daily_tracks = {}
        mmsi_found = False
        for mat_h5 in mat_h5s:
            try:
                ship = mat_h5.root._f_get_child('MMSI_' + mmsi_tgt)
                mmsi_found = True
            except:
                continue

            # collect the relavant messages
            for msgnum, gregtime in enumerate(ship.datenumber):
                msg_nanos = greg_to_nanos(gregtime[0])
                ymd = nanos_to_ymd_str(msg_nanos)
                lat = ship.LAT[msgnum][0]
                lon = ship.LON[msgnum][0]
                if daily_tracks.get(ymd) is None:
                    daily_tracks[ymd] = [(msg_nanos, lat, lon)]
                else:
                    daily_tracks[ymd].append((msg_nanos, lat, lon))

        if not mmsi_found:
            raise Exception("MMSI {} not found in .mat files")
            
        return daily_tracks
    '''
    period of time for a single vessel (individual for detection and buffer zones)
    df_mmsi_info is from the mmsi_scraper method
    '''
    def _mars_trips(
        self,
        mat_files, 
        df_mmsi_info, 
        buffer_zone_max, 
        detection_zone_max, 
        detection_zone_min=0.0
        ):

        colnames = ['MMSI', 'ZONE_ENTER', 'ZONE_EXIT', 'DESIG', 'CPA', 'CPA_TIME', 'MSG_INFO']
        df_trips_detect = pd.DataFrame(columns = colnames, dtype=object)
        df_trips_buffer = pd.DataFrame(columns = colnames, dtype=object)
        ship_zone = {}  # key = MMSI, value = current zone
        for f in mat_files: # each .mat file corresponds to a day's worth of AIS messages
            h5file = tables.open_file(f, mode = 'r')

            for i, ship in enumerate(h5file.root): # each ship
                if i > 0: # the first "ship" is garbage. ignore it.
                    mmsi = int(ship.MMSI[0][0])
                    # augment message info with additional web-scraped info
                    ship_data = df_mmsi_info.loc[df_mmsi_info['MMSI'] == mmsi] 
                    ship_desig = '' if ship_data.empty else ship_data["DESIG"].values[0]

                    # NOTE: messages are not in time-sorted order!!! sort them.
                    msgnum_nanos = []
                    for msgnum, gregtime in enumerate(ship.datenumber):
                        msgnum_nanos.append((msgnum, greg_to_nanos(gregtime[0])))
                    msgnum_nanos = sorted(msgnum_nanos, key=lambda x: x[1])

                    # iterate over the messages transmitted by a ship and formulate
                    # "trips" in the detection and buffer zones.
                    # NOTE: observing ~5-15 minutes between messages. TODO: more analysis
                    for msgnum, nanos in msgnum_nanos:
                        # ship.datenumber is an array that holds the time that 
                        # each AIS message was recorded, and each AIS message has
                        # info (LAT, LON, SOG, etc.) associated with it.
                        msg_time_nanos = nanos
                        lat = ship.LAT[msgnum][0]
                        lon = ship.LON[msgnum][0]
                        brg = get_bearing(lat, lon, SENSOR_LAT, SENSOR_LON)
                        rng = get_range(lat, lon, SENSOR_LAT, SENSOR_LON)
                        spd = int(ship.SOG[msgnum][0])

                        '''
                        A ship "trip" in a zone consists of:

                        MMSI
                        ZONE_ENTER - zone entrance time (nanos)
                        ZONE_EXIT - zone exit time (nanos)
                        DESIG - ship desig
                        CPA - ship closest point of approach to sensor (km)
                        CPA_TIME - time to cpa (nanos)
                        MSG_INFO - [[MSG_NANOS, LAT, LON, BRG, RNG, SOG], ...]

                        Note: A ship may enter and leave a zone more than once 
                        per day. Also, if a ships slows to < 1.0, then it falls out
                        of the detection and buffer zone, and into the no-ship
                        zone.
                        '''
                        # What zone is the ship in?
                        if detection_zone_min <= rng <= detection_zone_max and spd >= 1.0: # ship is in the detection zone
                            current_zone = DETECT_ZONE
                        elif detection_zone_max < rng <= buffer_zone_max and spd >= 1.0: # ship is in the buffer zone
                            current_zone = BUFFER_ZONE
                        else: # ship is in the NOSHIP zone
                            current_zone = NOSHIP_ZONE

                        # this is the start of a new trip if we've never seen this MMSI or the 
                        # previous observation of this MMIS was in a different zone.
                        # TODO: what if the ship turn off AIS and travel to another zone and then
                        # returns to this zone and retranmits AIS? Should we account for time
                        # between messages when constructing trips?
                        new_trip = not (mmsi in ship_zone) or (current_zone != ship_zone[mmsi])
                        # update the ship's zone
                        ship_zone[mmsi] = current_zone

                        # start a new trip, or update and existing trip
                        if ship_zone[mmsi] == DETECT_ZONE:
                            df_trips_detect = super().add_or_update_trip(df_trips_detect, new_trip, mmsi, msg_time_nanos, ship_desig, rng, lat, lon, brg, spd)
                        elif ship_zone[mmsi] == BUFFER_ZONE:
                            df_trips_buffer = super().add_or_update_trip(df_trips_buffer, new_trip, mmsi, msg_time_nanos, ship_desig, rng, lat, lon, brg, spd)
                        else: # ship is in the NOSHIP_ZONE. don't add or update any trips
                            continue
                            
            h5file.close()

        if len(df_trips_detect[df_trips_detect["ZONE_EXIT"] == 0]) > 0 or \
            len(df_trips_buffer[df_trips_buffer["ZONE_EXIT"] == 0]) > 0:
            raise Exception("Expected ZONE_EXIT times to be > 0")

        return df_trips_detect, df_trips_buffer

    def _get_trips(self,
                        user_start_nanos, 
                        user_end_nanos, 
                        detect_range, 
                        buffer_range, 
                        ais_data, 
                        mmsi_meta_cache):


        ts = time.time()
        mat_files = fetch_all_mat_files(ais_data, user_start_nanos, user_end_nanos)
        te = time.time()
        print("*** .mat file fetch = {} seconds".format(te - ts), flush=True)


        print("\n*** mmsi info from .mat files")
        ts = time.time()
        df_mmsi_info1 = mmsi_info_from_mat(mat_files = mat_files)
        te = time.time()
        print("*** columns in mmsi_info1 {}".format(df_mmsi_info1.columns))
        print("*** mmsi info from .mat files = {} seconds".format(te - ts), flush=True)


        print("\n*** augment mmsi with meta data", flush=True)
        ts = time.time()
        df_mmsi_info2 = mmsi_scraper(mmsis=df_mmsi_info1, mmsi_meta_cache=mmsi_meta_cache)
        te = time.time()
        print("*** columns in mmsi_info2 {}".format(df_mmsi_info2.columns))
        print("*** augment mmsi with meta data = {} seconds".format(te - ts), flush=True)


        print("\n*** ais trips df", flush=True)
        ts = time.time()
        df_trips_detect, df_trips_buffer = self._mars_trips(
            mat_files = mat_files, 
            df_mmsi_info = df_mmsi_info2,
            buffer_zone_max = detect_range+buffer_range, 
            detection_zone_max = detect_range,
            detection_zone_min = 0.0
            )
        te = time.time()
        print("*** ais trips df = {} seconds".format(te - ts), flush=True)
        
        return df_trips_detect, df_trips_buffer 
    

class Harp(Trips):
    def __init__(self,
                 user_start_nanos,
                 user_end_nanos, 
                 detect_range, 
                 buffer_range,
                 ais_data,
                 uscg_or_marine,
                 mmsi_meta_cache):
        Trips.__init__(self)
        print("AIS DATA PATH: ", ais_data)

        if uscg_or_marine == 'uscg':
            self.df_trips_detect, self.df_trips_buffer = self._get_harp_trips(user_start_nanos,
                                                                          user_end_nanos,
                                                                          detect_range,
                                                                          buffer_range,
                                                                          ais_data,
                                                                          mmsi_meta_cache)
        else:
            self.df_trips_detect, self.df_trips_buffer = self._get_marine_cadastre_harp_trips(user_start_nanos,
                                                                                              user_end_nanos,
                                                                                              detect_range,
                                                                                              buffer_range,
                                                                                              ais_data,
                                                                                              mmsi_meta_cache)
    
    def start_end_indices(self, uscg_file_nanos: list, user_start_nanos: int, user_end_nanos: int):
        start_index, end_index = -1, -1
        for i, nanos in enumerate(uscg_file_nanos):
            if user_start_nanos >= nanos:
                start_index = i
        for i, nanos in enumerate(uscg_file_nanos):
            if user_end_nanos >= nanos:
                end_index = i
        return start_index, end_index

    def _harp_trips(self,
            df_uscg_info: pd.DataFrame,
            df_mmsi_info: pd.DataFrame,
            buffer_zone_max: int,
            detection_zone_max: int,
            detection_zone_min: int=0):
        '''
        '''
        colnames = ['MMSI', 'ZONE_ENTER', 'ZONE_EXIT', 'DESIG', 'CPA', 'CPA_TIME', 'MSG_INFO']
        df_trips_detect = pd.DataFrame(columns = colnames, dtype=object)
        df_trips_buffer = pd.DataFrame(columns = colnames, dtype=object)
        ship_zone = {}


        for mmsi in df_uscg_info['MMSI'].unique():
            df_mmsi_query = df_mmsi_info.loc[df_mmsi_info['MMSI'] == f'{mmsi}']
            ship_desig = '' if df_mmsi_query.empty else df_mmsi_query['DESIG'].values[0]
            df_uscg_query = df_uscg_info.query("MMSI == @mmsi")
            for _, row in df_uscg_query.iterrows():
                if row['PERIOD'] == 'None' or row['LAT_AVG'] == 'None' or row['LON_AVG'] == 'None':
                    print('Some value was none, skipping row')
                    if row['PERIOD'] == 'None': print('period was none')
                    if row['LAT_AVG'] == 'None': print('lat was none')
                    if row['LON_AVG'] == 'None': print('lon was none')
                    if row['SPEED_KNOTS'] == 'None': print('speed was none')
                    # don't filter out ship if speed was none, just include and fill with 0
                    continue 
                time = uscg_date_to_nanos(row['PERIOD'])
                lat = row['LAT_AVG']
                lon = row['LON_AVG']
                brg = get_bearing(lat, lon, SENSOR_LAT, SENSOR_LON)
                rng = get_range(lat, lon, SENSOR_LAT, SENSOR_LON)
                spd = float(row['SPEED_KNOTS']) if row['SPEED_KNOTS'] != 'None' else 0.0 



                if detection_zone_min <= rng <= detection_zone_max and spd >= 1.0:
                    current_zone = DETECT_ZONE
                elif detection_zone_max < rng <= buffer_zone_max and spd >= 1.0:
                    current_zone = BUFFER_ZONE
                else:
                    current_zone = NOSHIP_ZONE
                
                new_trip = not (mmsi in ship_zone) or (current_zone != ship_zone[mmsi])

                ship_zone[mmsi] = current_zone

                if ship_zone[mmsi] == DETECT_ZONE:
                    df_trips_detect = super().add_or_update_trip(df_trips_detect, new_trip, mmsi, time, ship_desig, rng, lat, lon, brg, spd)
                elif ship_zone[mmsi] == BUFFER_ZONE:
                    df_trips_buffer = super().add_or_update_trip(df_trips_buffer, new_trip, mmsi, time, ship_desig, rng, lat, lon, brg, spd)
                else:
                    continue
        if len(df_trips_detect[df_trips_detect["ZONE_EXIT"] == 0]) > 0 or \
            len(df_trips_buffer[df_trips_buffer["ZONE_EXIT"] == 0]) > 0:
            raise Exception("Expected ZONE_EXIT times to be > 0")

        return df_trips_detect, df_trips_buffer
    
    def _marine_cadastre_harp_trips(self,
                                    df_marine_cadastre: pd.DataFrame,
                                    df_mmsi_info: pd.DataFrame,
                                    buffer_zone_max: int,
                                    detection_zone_max: int,
                                    detection_zone_min: int = 0
                                    ):
        colnames = ['MMSI', 'ZONE_ENTER', 'ZONE_EXIT', 'DESIG', 'CPA', 'CPA_TIME', 'MSG_INFO']
        df_trips_detect = pd.DataFrame(columns = colnames, dtype=object)
        df_trips_buffer = pd.DataFrame(columns = colnames, dtype=object)
        ship_zone = {}

        for mmsi in tqdm.tqdm(df_marine_cadastre['MMSI'].unique()):
            df_mmsi_query = df_mmsi_info.loc[df_mmsi_info['MMSI'] == f'{mmsi}']
            ship_desig = '' if df_mmsi_query.empty else df_mmsi_query['DESIG'].values[0]
            df_trip_info = df_marine_cadastre.loc[df_marine_cadastre['MMSI'] == mmsi].sort_values(by=['BaseDateTime'])
            for _, row in df_trip_info.iterrows():
                if row['BaseDateTime'] == 'None' or row['LAT'] == 'None' or row['LON'] == 'None':
                    print('Some value was none, skipping row')
                    if row['TIME_NANOS'] == 'None': print('time was none')
                    if row['LAT'] == 'None': print('lat was none')
                    if row['LON'] == 'None': print('lon was none')
                    if row['SOG'] == 'None': print('speed was none')
                    # don't filter out ship if speed was none, just include and fill with 0
                    continue 
                time = utc_to_nanos(row['BaseDateTime'])
                lat = row['LAT']
                lon = row['LON']
                brg = get_bearing(lat, lon, SENSOR_LAT, SENSOR_LON)
                rng = get_range(lat, lon, SENSOR_LAT, SENSOR_LON)
                spd = float(row['SOG']) if row['SOG'] != 'None' else 0.0 

                if detection_zone_min <= rng <= detection_zone_max and spd >= 1.0:
                    current_zone = DETECT_ZONE
                elif detection_zone_max < rng <= buffer_zone_max and spd >= 1.0:
                    current_zone = BUFFER_ZONE
                else:
                    current_zone = NOSHIP_ZONE
                
                new_trip = not (mmsi in ship_zone) or (current_zone != ship_zone[mmsi])

                ship_zone[mmsi] = current_zone

                if ship_zone[mmsi] == DETECT_ZONE:
                    df_trips_detect = super().add_or_update_trip(df_trips_detect, new_trip, mmsi, time, ship_desig, rng, lat, lon, brg, spd)
                elif ship_zone[mmsi] == BUFFER_ZONE:
                    df_trips_buffer = super().add_or_update_trip(df_trips_buffer, new_trip, mmsi, time, ship_desig, rng, lat, lon, brg, spd)
                else:
                    continue
        if len(df_trips_detect[df_trips_detect["ZONE_EXIT"] == 0]) > 0 or \
            len(df_trips_buffer[df_trips_buffer["ZONE_EXIT"] == 0]) > 0:
            raise Exception("Expected ZONE_EXIT times to be > 0")

        return df_trips_detect, df_trips_buffer 

    def _get_marine_cadastre_harp_trips(self,
                                        user_start_nanos: int,
                                        user_end_nanos: int,
                                        detect_range: int,
                                        buffer_range: int,
                                        marine_cadastre_ais_path: str,
                                        mmsi_meta_cache: str):
        sorted_file_list = sorted(os.listdir(marine_cadastre_ais_path))
        file_nanos = [marine_cadastre_to_nanos(fn) for fn in sorted_file_list]
        start_index, end_index = self.start_end_indices(file_nanos, user_start_nanos, user_end_nanos)
        ais_files = sorted_file_list[start_index:end_index+1]
        df_marine_cadastre_data = []

        for i, ais_file in enumerate(ais_files):
            df_ais_file = pd.read_csv(marine_cadastre_ais_path + ais_file, on_bad_lines='skip')
            df_ais_file['TIME_NANOS'] = df_ais_file['BaseDateTime'].apply(utc_to_nanos)
            if i == 0:
                df_ais_file = df_ais_file.query("TIME_NANOS >= @user_start_nanos")
            if i == len(ais_files) - 1:
                df_ais_file = df_ais_file.query("TIME_NANOS <= @user_end_nanos")
            df_marine_cadastre_data.append(df_ais_file)

        df_marine_cadastre = pd.concat(df_marine_cadastre_data, ignore_index=True)
        df_mmsi_info = df_marine_cadastre[['MMSI', 'IMO', 'VesselType']].drop_duplicates()
        df_mmsi_info = df_mmsi_info.rename(columns={"VesselType": "Ship Type"})
        df_mmsi_info = mmsi_scraper(mmsis=df_mmsi_info, mmsi_meta_cache=mmsi_meta_cache)
        df_trips_detect, df_trips_buffer = self._marine_cadastre_harp_trips(
            df_marine_cadastre=df_marine_cadastre,
            df_mmsi_info=df_mmsi_info,
            buffer_zone_max=detect_range + buffer_range,
            detection_zone_max=detect_range,
            detection_zone_min=0
        )         
        df_trips_detect['CLASS'] = df_trips_detect['DESIG'].apply(get_desig_class)
        df_trips_buffer['CLASS'] = df_trips_buffer['DESIG'].apply(get_desig_class)
        return df_trips_detect, df_trips_buffer
        
    def _get_harp_trips(self,
                    user_start_nanos: int, 
                    user_end_nanos: int,
                    detect_range: int,
                    buffer_range: int,
                    uscg_ais_path: str,
                    mmsi_meta_cache: str):
        uscg_sorted_file_list = sorted(os.listdir(uscg_ais_path))
        # get all the relevant uscg ais csv files and place them in a list
        uscg_file_nanos = [uscg_ais_to_nanos(filename) for filename in uscg_sorted_file_list]
        # - find the indices of the start and end nanos in uscg_file_nanos. This will give us the range of csv files to work with
        start_index, end_index = self.start_end_indices(uscg_file_nanos, user_start_nanos, user_end_nanos)
        # select the subsection of files
        ais_files = uscg_sorted_file_list[start_index:end_index+1]
        df_uscg_info_data = []
        # process all the csv files and place in a dataframe
        for i, ais_file in enumerate(ais_files):
            # check for start time to concat
            # first file will always be start time
            df_ais_file = pd.read_csv(uscg_ais_path + ais_file)
            df_ais_file['PERIOD_NANOS'] = df_ais_file['PERIOD'].apply(uscg_date_to_nanos)
            if i == 0:
                # check for start time
                df_ais_file = df_ais_file.query("PERIOD_NANOS >= @user_start_nanos")
            if i == len(ais_files) - 1:
                # check for end time
                df_ais_file = df_ais_file.query("PERIOD_NANOS <= @user_end_nanos")
            
            df_uscg_info_data.append(df_ais_file)

            # check for end time to concat
        df_uscg_info = pd.concat(df_uscg_info_data, ignore_index=True)
        # df_uscg_info = pd.concat([pd.read_csv(uscg_ais_path + file) for file in ais_files], ignore_index=True)
        df_mmsi_info = df_uscg_info[['MMSI', 'IMO_NUMBER', 'SHIP_AND_CARGO_TYPE']].drop_duplicates()
        df_mmsi_info = df_mmsi_info.rename(columns={'IMO_NUMBER': 'IMO', 'SHIP_AND_CARGO_TYPE': 'Ship Type'})
        
        # augment data in current dataframe with mmsi_scraper
        df_mmsi_info = mmsi_scraper(mmsis=df_mmsi_info, mmsi_meta_cache=mmsi_meta_cache)
        # create df_trips_detect and df_trips_buffer
        df_trips_detect, df_trips_buffer = self._harp_trips(
            df_uscg_info=df_uscg_info,
            df_mmsi_info=df_mmsi_info,
            buffer_zone_max=detect_range + buffer_range,
            detection_zone_max=detect_range,
            detection_zone_min=0
        )

        return df_trips_detect, df_trips_buffer

