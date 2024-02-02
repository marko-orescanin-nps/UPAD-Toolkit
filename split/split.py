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

    num_examples = 0
    print('getting train start and end')
    train_start_0, train_end_0 = user_date_to_nanos('20190201 000000'), user_date_to_nanos('20191231 235959')
    print('train_0 query')
    train_query_0 = Query(records_dir = records_dir, tfrecords_pkl=tfrecords_pkl).get_time(train_start_0, train_end_0)
    num_examples += len(train_query_0.tfrecords)
    with open(output_path + 'train.txt', 'w+') as f:
        for tfrecord in train_query_0.tfrecords:
            f.write(tfrecord + '\n')
    del train_query_0
    print('getting train start and end')
    train_start_1, train_end_1 = user_date_to_nanos('20200101 000000'), user_date_to_nanos('20210601 000000')
    print('train_1 query')
    train_query_1 = Query(records_dir = records_dir, tfrecords_pkl=tfrecords_pkl).get_time(train_start_1, train_end_1)
    num_examples += len(train_query_1.tfrecords)
    with open(output_path + 'train.txt', 'a+') as f:
        for tfrecord in train_query_1.tfrecords:
            f.write(tfrecord + '\n')
    del train_query_1

    for i in range(6, 13):
        split_len = int((last_day_of_month[i] - 2) / 2)
        month = convert_single_digit(i)

        test_end_day   = last_day_of_month[i]
        test_start_day = test_end_day - split_len
        val_end_day    = test_start_day - 1
        val_start_day  = 2

        val_start_day  = convert_single_digit(val_start_day)
        val_end_day    = convert_single_digit(val_end_day)
        test_start_day = convert_single_digit(test_start_day)
        test_end_day   = convert_single_digit(test_end_day)

        val_start, val_end = user_date_to_nanos(f'2021{month}{val_start_day} 000000'), \
                             user_date_to_nanos(f'2021{month}{val_end_day} 235959')
        test_start, test_end = user_date_to_nanos(f'2021{month}{test_start_day} 000000'), \
                               user_date_to_nanos(f'2021{month}{test_end_day} 235959')
        print(val_start, val_end)
        val_query = Query(records_dir = records_dir, tfrecords_pkl = tfrecords_pkl).get_time(val_start, val_end)
        num_examples += len(val_query.tfrecords)
        with open(output_path + 'validate.txt', 'a+') as f:
            for tfrecord in val_query.tfrecords:
                f.write(tfrecord + '\n')
        
        del val_query

        test_query = Query(records_dir = records_dir, tfrecords_pkl = tfrecords_pkl).get_time(test_start, test_end)
        num_examples += len(test_query.tfrecords)
        with open(output_path + 'test.txt', 'a+') as f:
            for tfrecord in test_query.tfrecords:
                f.write(tfrecord + '\n')
        
        del test_query