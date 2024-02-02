import argparse as ap
import os
from utils.tfrecord_utils import translate_record_to_label

def count_ship_no_ship(labels):
    ship_cnt = no_ship_cnt = 0
    for label in labels:
        if '1' in label[5]:
            no_ship_cnt += 1
        else:
            ship_cnt += 1
    return ship_cnt, no_ship_cnt

def count_multilabel(labels):
    a = b = c = d = e = f = 0
    for label in labels:
        if '1' in label[0]:
            a += 1
        if '1' in label[1]:
            b += 1
        if '1' in label[2]:
            c += 1
        if '1' in label[3]:
            d += 1
        if '1' in label[4]:
            e += 1
        if '1' in label[5]:
            f += 1

    return a, b, c, d, e, f

def write_stats(split_dir, section):
    with open(split_dir + f'/{section}.txt', 'r') as f:
        labels = [translate_record_to_label(record) for record in f.readlines()]
        with open(split_dir + f'/{section}/stats.txt', 'w+') as output:
            ship_cnt, no_ship_cnt = count_ship_no_ship(labels)
            output.write(f"{ship_cnt}, {no_ship_cnt}")

def write_multilabel_stats(split_dir, section):
    with open(split_dir + f'/{section}.txt', 'r') as f:
        labels = [translate_record_to_label(record) for record in f.readlines()]
        with open(split_dir + f'/{section}/multilabel_counts.txt', 'w+') as output:
            a, b, c, d, e, f = count_multilabel(labels)
            output.write(f'{a}, {b}, {c}, {d}, {e}, {f}')

if __name__ == '__main__':
    parser = ap.ArgumentParser()

    parser.add_argument("--split_dir",
                        required=True)
    
    args = parser.parse_args()
    split_dir = args.split_dir
    # write_stats(split_dir, 'full_train')
    # write_stats(split_dir, 'full_upsample_train')
    # write_stats(split_dir, 'full_even_test')
    # write_stats(split_dir, 'full_even_validate')
    # write_stats(split_dir, 'test_6_month')
    write_multilabel_stats(split_dir, 'full_train')
    write_multilabel_stats(split_dir, 'full_upsample_train')
    write_multilabel_stats(split_dir, 'full_even_test')
    write_multilabel_stats(split_dir, 'full_even_validate')
    write_multilabel_stats(split_dir, 'test_6_month')
