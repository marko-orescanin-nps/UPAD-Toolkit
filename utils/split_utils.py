from tqdm import tqdm
from utils.tfrecord_utils import translate_record_to_label

import random

def split_individual_label_counts(filename: str):
    '''
    Description: gets label counts based on binary classification (ship/no_ship)

    :filename: txt file containing list of tfrecords

    :returns: ship present count/no ship present count
    '''
    ship_counts = no_ship_counts = 0
    with open(filename, 'r') as f:
        lines = [line.rstrip() for line in f]
        for line in tqdm(lines):
            a_label, b_label, c_label, d_label, e_label = translate_record_to_label(line)
            if '1' in e_label:
                no_ship_counts += 1
            else:
                ship_counts += 1
    return ship_counts, no_ship_counts

def split_counts(filename: str) -> dict:
    '''
    Description: gets counts of each class (multi-class count)

    :filename: txt file containing list of tfrecords 

    :returns: a dictionary of counts in a split file
    '''
    with open(filename, 'r') as f:
        lines = [line.rstrip() for line in f]
        counts = {
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0,
            'E': 0,
            'F': 0
        }
        for line in tqdm(lines):
            a_label, b_label, c_label, d_label, e_label, f_label = translate_record_to_label(line)
            
            if '1' in a_label:
                counts['A'] += 1
            if '1' in b_label:
                counts['B'] += 1
            if '1' in c_label:
                counts['C'] += 1
            if '1' in d_label:
                counts['D'] += 1
            if '1' in e_label:
                counts['E'] += 1
            if '1' in f_label:
                counts['F'] += 1
        print(counts)
        return counts
    
def upsample(split_filename: str, output_filename: str, rate=5):
    '''
    Description: Upsamples ship present tfrecords in split file based on rate and ship/no ship ratio
    :split_filename: split file with tfrecords
    :output_filename: designated output file
    :rate: factor to upsample by

    :returns: None
    '''
    if rate == 0:
        with open(output_filename, 'w+') as output_file, open(split_filename, 'r') as split_file:
            for line in split_file:
                output_file.write(line)
        return
    print('getting original counts')
    split_counts(split_filename)
    files = []
    with open(split_filename, 'r') as split_file:
        lines = [line.rstrip() for line in split_file]
        for line in tqdm(lines):
            _, _, _, _, _, f_label = translate_record_to_label(line) 
            if '1' not in f_label:
                for _ in range(rate):
                    files.append(line)
            else:
                files.append(line)

    
    with open(output_filename, 'w+') as output_file:
        for file in files:
            output_file.write(file + '\n')
            
    print('upsampled counts')
    split_counts(output_filename)

def downsample(split_filename: str, output_filename: str, rate=1):
    '''
    Description: downsamples the number of no ship examples to the number of ship samples. Rate indicates how many times more no ship there should be than ship (rate=1 means equal amount)
    
    :split_filename: split file with tfrecords
    :output_filename: designated output file
    :rate: factor to downsample by
    
    :returns: None
    '''
    if rate == 0:
        with open(output_filename, 'w+') as output_file, open(split_filename, 'r') as split_file:
            for line in split_file:
                output_file.write(line)
        return
        
    print('getting original counts')
    counts = split_counts(split_filename)

    ship_counts = counts['A'] + counts['B'] + counts['C'] + counts['D']
    ship_files = []
    no_ship_files = []
    with open(split_filename, 'r') as split_file:
        lines = [line.rstrip() for line in split_file]
        for line in tqdm(lines):
            _, _, _, _, e_label = translate_record_to_label(line) 
            if '1' in e_label:
                no_ship_files.append(line)
            else:
                ship_files.append(line)

    num_samples_of_no_ship_counts = ship_counts * rate
    new_no_ship_files = random.sample(no_ship_files, num_samples_of_no_ship_counts)

    all_ship_files = new_no_ship_files + ship_files
    print('writing new samples to file')
    with open(output_filename, 'w+') as output_file:
        for file in all_ship_files:
            output_file.write(file + '\n')

    print('displaying new counts')
    split_counts(output_filename)



