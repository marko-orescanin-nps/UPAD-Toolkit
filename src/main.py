import argparse

import time
from src.audio_fetch import AudioFetcher
from src.ais import Harp, Mars

from utils.time_utils import user_date_to_nanos
from utils.tfrecord_utils import record_writer

def get_avg_brg_rng(audio_start_nanos, track):
    ''' 
    Description: Compute the average bearing and range of this 30-second segment \n
    starting at `audio_start_nanos`. 

    NOTE: AIS messages appear to arrive every 5-15 minutes (not very high
    resolution). Just grab the closest message to `audio_start_nanos` and set
    the avg_brg to the bearing is this message. TODO: verify AIS message resolution
    and if we encounter higher resolution, then adjust the logic of this 
    function.\n

    :audio_start_nanos: start timestamp of the segment to get information from\n
    :track: trip information to pull information for bearing and range\n
    :returns: average bearing and range\n
    '''
    msg_times = [t[0] for t in track]
    idx = min(range(len(msg_times)), key=lambda i: abs(msg_times[i]-audio_start_nanos))
    # message schema: (msg_time_nanos, lat, lon, brg, rng, spd)
    avg_brg, avg_rng = track[idx][3], track[idx][4]
    return avg_brg, avg_rng

def audio_shape_check(audio_shape, wav_fmt):
    if wav_fmt == 'mars' and audio_shape != (4, 120000):
        # raise Exception(f'Invalid Audio Shape of {audio_shape}')
        return False
    # assertion: segment have appropriate shape for harp data. Figure out what the shape is
    elif wav_fmt == 'harp' and audio_shape != (1, 120000):
        # raise Exception(f'Invalid Audio Shape of {audio_shape}')
        return False
    return True


    
def label_segment(df_trips_detect_segment, df_trips_buffer_segment, audio_start_nanos):
    '''
    Description: Returns label_info and class counts
    :df_trips_detect_segment:
    :df_trips_buffer_segment:
    :audio_start_nanos:
    '''
    cur_count = {"Class A": 0, "Class B": 0, "Class C": 0, "Class D": 0, "Class E": 0, "Class F": 0} 
    # don't label if df_trips_buffer has any trips
    if len(df_trips_buffer_segment) > 0:
        print("skipping segment")
        return
    else:
        label_info = []

        if len(df_trips_detect_segment) == 0:
            # Right now every df_trips_detect_segment that is being generated is completely empty for HARPS
            # Has to do with differences between time filter for harp vs mars
            print("registered a class F")
            cur_count['Class F'] = 1

        else:
            for _, trip in df_trips_detect_segment.iterrows():
                print(trip['DESIG'])
                # TODO: check if Ship was actually moving (keep track of ship tracks)
                ship_class = trip['CLASS']
                brg, rng = get_avg_brg_rng(audio_start_nanos, trip['MSG_INFO'])
                mmsi = trip['MMSI']
                desc = trip['DESIG'].encode('utf-8')

                label_info.append([ship_class, brg, rng, mmsi, desc])

                if cur_count[ship_class] == 0:
                    cur_count[ship_class] = 1
        return label_info, cur_count



def main(
    tfrecord_audio, 
    ais_data, 
    tfrecord_dir, 
    mono, 
    sample_rate,
    detect_range,
    buffer_range, 
    start, 
    end, 
    mmsi_meta_cache,
    wav_dir,
    wav_fmt,
    segment_length_seconds,
    uscg_or_marine
    ):
    '''
    Description: main function for multilabel tfrecord generation \n
    :tfrecord_audio: 'raw | mel' \n
    :ais_data: directory of ais data\n
    :tfrecord_dir: directory to store tfrecords\n
    :mono: True | False\n
    :sample_rate: sample rate of the input audio\n
    :detect_range: range in km, ships in range show up as labels\n
    :buffer_range: range in km, offset from detect_range\n
    :start: start time in UTC timezone in format YYYYMMDD HHMMSS \n
    :end: end time in UTC timezone in format YYYYMMDD HHMMSS\n
    :mmsi_meta_cache: path to csv file containing mmsi info\n
    :wav_dir: directory containing wav data\n
    :wav_fmt: 'mars | help'\n
    :segment_length_seconds: time in seconds for segment (30 s)\n
    '''

    # Note on timezones:
    # `start` and `end` are UTC timezone in format YYYYMMDD HHMMSS
    # .mat filenames (i.e. 180406.mat) are in UTC timezone
    # .mat datenumber field are in proleptic Gregorian ordinal format in UTC timezone 
    # .wav filenames (m209_oxyz_20190123005827.wav) are in UTC timezone
    # The above EXTERNAL times are converted to nanoseconds since the epoch. 
    # All INTERNAL times are nanoseconds since the epoch.
    user_start_nanos = user_date_to_nanos(start)
    user_end_nanos = user_date_to_nanos(end)
    if wav_fmt == 'mars':
        trip = Mars(user_start_nanos,
                    user_end_nanos,
                    detect_range,
                    buffer_range,
                    ais_data,
                    mmsi_meta_cache
                    )
    elif wav_fmt == 'harp':
        trip = Harp(user_start_nanos,
                    user_end_nanos,
                    detect_range,
                    buffer_range,
                    ais_data,
                    uscg_or_marine,
                    mmsi_meta_cache)
        
    # print("this is the length of the df_trips_detect: " + len(trip.df_trips_detect))

    df_trips_detect, df_trips_buffer = trip.df_trips_detect, trip.df_trips_buffer

    print("instantiate audio fetcher")
    interval = [user_start_nanos, user_end_nanos]
    ts = time.time()
    af = AudioFetcher(interval, wav_dir=wav_dir, wav_fmt=wav_fmt, sample_rate=sample_rate, segment_length_seconds=segment_length_seconds)
    te = time.time()
    print("instantiate audio fetcher = {} seconds".format(te - ts))

    print("tfrecords for group")
    ts_tfrecords = time.time()
    tfrecord_cnt = 0

    print("generating segments")
    ts = time.time()
    af.generate_wav_segments()
    print(f'finished generating segments = {time.time() - ts} seconds')
    
    # process each segment
    # TODO: speed up process by multithreading
    for i, segment in enumerate(af.wav_segments, 1):
        print(f"{i}/{len(af.wav_segments)}")
        audio_start_nanos, audio = segment

        if not audio_shape_check(audio.shape, wav_fmt):
            print(audio.shape, "shape was incorrect")
            continue


        df_trips_detect_segment = trip.time_filter_df_trips(df_trips_detect,
                                                audio_start_nanos,
                                                audio_start_nanos + 30e9)
        df_trips_buffer_segment = trip.time_filter_df_trips(df_trips_buffer,
                                                audio_start_nanos,
                                                audio_start_nanos + 30e9)
        print(f"Lengths of segments: detect {len(df_trips_detect_segment)} buffer {len(df_trips_buffer_segment)}")

        label = label_segment(df_trips_detect_segment, df_trips_buffer_segment, audio_start_nanos)
        if label is None:
            continue
        label_info, cur_count = label

        unique_id = '{:f}_{:f}'.format(audio_start_nanos, audio_start_nanos+30e9)
        a_count = cur_count['Class A']
        b_count = cur_count['Class B']
        c_count = cur_count['Class C']
        d_count = cur_count['Class D']
        e_count = cur_count['Class E']
        f_count = cur_count['Class F']
        record_path = f"{tfrecord_dir}{unique_id}_A{a_count}_B{b_count}_C{c_count}_D{d_count}_E{e_count}_F{f_count}.tfrecord"
        print(f'writing the record: {record_path}')
        record_writer(record_path, audio, label_info, unique_id)
        print('finished writing the record')
        tfrecord_cnt += 1
    
    tfrecord_hrs = 30 * tfrecord_cnt / 3600
    print("Wrote {} tfrecords ({} * 30 seconds = {} hrs)".format(tfrecord_cnt, tfrecord_cnt, tfrecord_hrs))
    print("tfrecords = {} seconds".format(time.time() - ts_tfrecords))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--tfrecord_audio', 
        type=str,   
        required=True,
        help="[raw|mel]"
        )
    parser.add_argument(
        '--ais_data',   
        type=str,     
        required=True,                        
        help="location of AIS .mat files"
        )
    parser.add_argument(
        '--tfrecord_dir',
        type=str,   
        required=True,
        help="location of produced tfrecords"
        )
    parser.add_argument(
        '--mmsi_meta_cache',   
        type=str,
        required=False,              
        help="path to mmsi metadata file"
        )
    parser.add_argument(
        '--wav_dir',   
        type=str,
        required=True,              
        help="directory where .wav files exist"
        )
    parser.add_argument(
        '--wav_fmt',   
        type=str,
        required=True,              
        help="[mars|harp]. .wav filename schema to use (see audio_fetch.py)."
        )
    parser.add_argument(
        '--mono',     
        action='store_true',
        help="passed to librosa.load as `mono` argument. False if left \
            unspecified."
        )
    parser.add_argument(
        '--sample_rate',  
        type=int,   
        required=True,               
        help="passed to librosa.load as `sr` argument"
        )
    parser.add_argument(
        '--calibrate',     
        action='store_true',
        help="calibrate 4-channel audio time series. False if left \
            unspecified."
        )
    parser.add_argument(
        '--detect_range',  
        type=float,   
        required=True,               
        help="radius of detection zone"
        )
    parser.add_argument(
        '--buffer_range',  
        type=float,   
        required=True,               
        help="offset of detection zone"
        )
    parser.add_argument(
        '--start',   
        type=str,
        required=True,                             
        help="start date/time in format YYYYMMDD HHMMSS"
        )
    parser.add_argument(
        '--end',     
        type=str, 
        required=True,                            
        help="end date/time in format YYYYMMDD HHMMSS"
        )
    parser.add_argument(
        '--segment_length_seconds',
        type=int,
        required=True,
        help="length of time to label"
    )
    parser.add_argument(
        '--uscg_or_marine',
        type=str,
        required=True,
        help="generate using uscg vs marine cadastre ais data"
    )

    args = parser.parse_args()

    main(
        args.tfrecord_audio, 
        args.ais_data, 
        args.tfrecord_dir, 
        args.mono, 
        args.sample_rate,
        args.detect_range,
        args.buffer_range, 
        args.start, 
        args.end, 
        args.mmsi_meta_cache,
        args.wav_dir,
        args.wav_fmt,
        args.segment_length_seconds,
        args.uscg_or_marine
        )
