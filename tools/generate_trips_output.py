from utils.time_utils import user_date_to_nanos
from src.ais import Harp

import argparse


ais_data = '/data/kraken/teams/acoustic_data/ais_data_labeling/ais_data/MarineCadastre_0/'
mmsi_meta_cache = '/data/kraken/teams/acoustic_data/ais_data_labeling/mmsi_meta_cache/MarineCadastre/cache.csv'

uscg_or_marine = 'marine'

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--start',
        type=str,
        required=True
    )
    ap.add_argument(
        '--end',
        type=str,
        required=True
    )
    ap.add_argument(
        '--detect',
        type=float,
        required=True
    )
    ap.add_argument(
        '--buffer',
        type=float,
        required=True
    )

    ap.add_argument(
        '--year',
        type=str,
        required=True
    )
    ap.add_argument(
        '--month',
        type=str,
        required=True
    )
    ap.add_argument(
        '--portion',
        type=int,
        required=True
    )

    args = ap.parse_args()

    start_nanos = user_date_to_nanos(args.start)
    end_nanos = user_date_to_nanos(args.end)
    detect_range = args.detect
    buffer_range = args.buffer
    month = args.month
    year = args.year
    portion = args.portion



    trip = Harp(start_nanos,
                end_nanos,
                detect_range,
                buffer_range,
                ais_data,
                uscg_or_marine,
                mmsi_meta_cache)

    trip.df_trips_detect.to_csv(f"samples/{detect_range}_{buffer_range}/{month}_{year}_{portion}_{detect_range}_{buffer_range}.csv", index=False)
