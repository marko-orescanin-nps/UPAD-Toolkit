from pytz import timezone
from utils.time_utils import mat_filename_to_nanos, nanos_to_ymd_str
import os
import glob
import pandas as pd
import tables


'''
fetch_mat_file

if only ais_data_file_path is passed, then we return all mat files in the file path

if start_nanos is provided, we provide all mat files that start with the date

if end nanos is provided, we provide all mat files that end with the date

if nanos_list is provided, we provide all mat files that come after 
'''
def fetch_mat_file(ais_data_file_path,
                   start_nanos=None,
                   end_nanos=None):
    mat_files = []
    all_mats = glob.glob(os.path.join(ais_data_file_path, '*.mat'))
    for mat in all_mats:
        # check if the file exists
        if not os.path.exists(mat):
            raise Exception("Expected {} to exist".format(mat))
        # get the start and end times from the filenames 
        mat_start_nanos = mat_filename_to_nanos(mat.split('/')[-1])
        mat_stop_nanos  = mat_start_nanos + 24*3600*10**9

        # generate the return value
        append_val = (mat_start_nanos, os.path.join(ais_data_file_path, mat))

        if start_nanos is not None and end_nanos is not None:
            if end_nanos > mat_start_nanos and start_nanos < mat_stop_nanos:
                mat_files.append(append_val) 
        elif start_nanos is not None:
            if start_nanos == mat_start_nanos:
                mat_files.append(append_val)
        elif end_nanos is not None:
            if end_nanos == mat_stop_nanos:
                mat_files.append(append_val)
        else:
            mat_files.append(append_val)
    mat_files = sorted(mat_files, key=lambda x: x[0])
    mat_files = [filepath for _, filepath in mat_files]
    return mat_files

def fetch_all_mat_files(ais_data, start_nanos, end_nanos):
    all_mats = glob.glob(os.path.join(ais_data, '*.mat'))
    mat_files = []
    for mat in all_mats:
        mat_start_nanos = mat_filename_to_nanos(mat.split('/')[-1])
        mat_stop_nanos  = mat_start_nanos + 24*3600*10**9
        overlap = not ((end_nanos < mat_start_nanos) or (start_nanos > mat_stop_nanos))
        if overlap:
            mat_files.append((mat_start_nanos, os.path.join(ais_data, mat)))
    mat_files = sorted(mat_files, key=lambda x: x[0])
    mat_files = [filepath for _, filepath in mat_files]
    return mat_files
    
def fetch_some_mat_files(ais_data_file_path, starts_nanos):
    starts_dates = set()
    for n in starts_nanos:
        # AIS .mat files in format YYMMDD.mat
        ymd = nanos_to_ymd_str(n)
        starts_dates.add(ymd)

    mat_files = []
    for dt in starts_dates:
        mat_file = os.path.join(ais_data_file_path, dt + '.mat')
        if not os.path.exists(mat_file):
            raise Exception("Expected {} to exist".format(mat_file))
        mat_files.append(mat_file)
    return mat_files    

def mmsi_info_from_mat(mat_files):
    """ Create single dataframe of MMSI, IMO, Ship Type from .mat files"""

    mmsis = {}
    for mat in mat_files:
        # store in key = time stamp, value = list of MMSI, range, brg
        h5file = tables.open_file(mat, mode = 'r') # TODO: Why are we using tables package to read .mat files?
        for i, ship in enumerate(h5file.root):
            imo = 0
            sType = 0
            if i > 0:
                mmsi = int(ship.MMSI[0][0])
                if 'IMOnumber' in ship:
                    imo = int(ship.IMOnumber[0][0])
                if 'ShipType' in ship:
                    sType = int(ship.ShipType[0][0])
                # if mmsi not found yet, add to list
                if mmsi not in mmsis:
                    mmsis[mmsi] = [mmsi, imo, sType]
        h5file.close()

    df = pd.DataFrame.from_dict(
        mmsis, 
        orient= 'index',
        columns=["MMSI", "IMO", "Ship Type"]
        ) 
    df = df.reset_index().drop('index', axis=1)
    return df
