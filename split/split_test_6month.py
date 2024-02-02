# create new splits. First two years should be the training section,
# and for the last year split each month in half for validation and test
from utils.time_utils import user_date_to_nanos, convert_single_digit
from utils.query_utils import get_individual_label_counts, combine_mmsis, combine_desc, start_end_times
from query.query import Query

import argparse


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

    test_start, test_end = user_date_to_nanos('20210601 000000'), user_date_to_nanos('20211231 235959')
    test_query = Query(records_dir = records_dir, tfrecords_pkl=tfrecords_pkl).get_time(test_start, test_end)
    with open(output_path + 'test_6_month.txt', 'w+') as f:
        print(len(test_query.tfrecords))
        for tfrecord in test_query.tfrecords:
            print(tfrecord)
            f.write(tfrecord + '\n')
    del test_query
    
