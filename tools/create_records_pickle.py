import os
import pickle
import argparse

from utils.tfrecord_utils import translate_record_to_interval, translate_record_to_label

def create_records_pickle(record_dir: str, output_pickle: str):
    result = []
    for record in sorted(os.listdir(record_dir)):
        result.append([translate_record_to_interval(record), translate_record_to_label(record)])
    with open(output_pickle, 'wb') as f:
        pickle.dump(result, f)
    

if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument("--record_dir", required=True)
    ap.add_argument("--output_pickle", required=True)
    args = ap.parse_args()
    create_records_pickle(args.record_dir, args.output_pickle)

