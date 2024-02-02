# create new splits, test and validate over 6 months. splits should have even number of samples
from utils.time_utils import user_date_to_nanos 
from utils.tfrecord_utils import translate_record_to_label
from query.query import Query

import argparse
import random


last_day_of_month = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


if __name__ == '__main__':
    print('parsing arguments')
    ap = argparse.ArgumentParser()
    ap.add_argument('--records_dir', required=True, help='location of records')
    ap.add_argument('--tfrecords_pkl', required=True, help='tfrecord intervals')
    ap.add_argument("--output_path", required=True, help="Folder to place training splits")
    args = vars(ap.parse_args())

    records_dir = args['records_dir']
    tfrecords_pkl = args['tfrecords_pkl']
    output_path = args['output_path']

    query_start, query_end = user_date_to_nanos('20210601 000000'), user_date_to_nanos('20211231 235959')
    query = Query(records_dir = records_dir, tfrecords_pkl=tfrecords_pkl).get_time(query_start, query_end)
    # sort all tfrecords by class

    label_record = {}

    for tfrecord in query.tfrecords:
        label = translate_record_to_label(tfrecord)
        if label in label_record:
            label_record[label].append(tfrecord)
        else:
            label_record[label] = []
    
    val_records, test_records = [], []

    for key, value in label_record.items():
        random.shuffle(value)
        half = len(value) // 2
        val_records.extend(value[:half])
        test_records.extend(value[half:])


    with open(output_path + 'even_validate.txt', 'w') as f:
        for record in val_records:
            f.write(record + '\n')
    with open(output_path + 'even_test.txt', 'w') as f:
        for record in test_records:
            f.write(record + '\n')