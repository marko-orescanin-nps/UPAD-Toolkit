import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # disable tensorflow logs

from IPython.display import Audio
import pandas as pd
import numpy as np

from utils.tfrecord_utils import parse_tfrecord, get_audio

class Query():
    def __init__(self, records_dir, tfrecords_pkl):
        self.records_dir = records_dir
        self.file_info = pd.read_pickle(tfrecords_pkl)
        self.records_intervals = [file[0] for file in self.file_info]
        self.labels = [file[1] for file in self.file_info]
        self.tfrecords = ['{:f}_{:f}_{}_{}_{}_{}_{}_{}.tfrecord'.format(interval[0], interval[1], label[0], label[1], label[2], label[3], label[4], label[5]) for interval, label in zip(self.records_intervals, self.labels)]
        
    def __add__(self, q):
        '''
        adds two querys together
        :q: other query
        '''
        query = Query(records_dir=self.records_dir, tfrecords_pkl=self.tfrecords_pkl)
        # we need to guarantee no duplicates in records intervals and tfrecords
        query.records_intervals = self.records_intervals
        for interval in q.records_intervals:
            if interval not in query.records_intervals:
                query.records_intervals.append(interval)
        
        query.tfrecords = self.tfrecords
        for tfrecord in q.tfrecords:
            if tfrecord not in query.tfrecords:
                query.tfrecords.append(tfrecord)
        
        return query
    
    def __search(self, time_nanos: float):
        '''
        Searches and returns index where time_nanos is in intervals
        :time_nanos: time to search in intervals list (nanoseconds)
        '''
        for i, interval in enumerate(self.records_intervals):
            if interval[0] <= time_nanos < interval[1] or time_nanos < interval[0]:
                return i
        return -1

    def get_time(self, start_time_nanos: float, end_time_nanos: float):
        '''
        Grab all tfrecords in between start_time_nanos and end_time_nanos\n
        :start_time_nanos: time in nanos to start grabbing from \n
        :end_time_nanos: time in nanos to end. If None grab all until run out of tfrecords to grab \n
        '''
        start_interval_idx = self.__search(start_time_nanos)
        end_interval_idx = self.__search(end_time_nanos)
        print("start and end index: {} {}".format(start_interval_idx, end_interval_idx))
        
        self.records_intervals = self.records_intervals[start_interval_idx:end_interval_idx]
        self.labels = self.labels[start_interval_idx:end_interval_idx]
        self.tfrecords = ['{:f}_{:f}_{}_{}_{}_{}_{}_{}.tfrecord'.format(interval[0], interval[1], label[0], label[1], label[2], label[3], label[4], label[5]) for interval, label in zip(self.records_intervals, self.labels)]
        
        return self
    
    def get_label(self, query_label: str):
        # get indices of elements within label with marked label
        indices = []
        for i, label in enumerate(self.labels):
            a_flag, b_flag, c_flag, d_flag, e_flag, f_flag = label
            if query_label == 'A' and '1' in a_flag:
                indices.append(i)
            if query_label == 'B' and '1' in b_flag:
                indices.append(i)
            if query_label == 'C' and '1' in c_flag:
                indices.append(i)
            if query_label == 'D' and '1' in d_flag:
                indices.append(i)
            if query_label == 'E' and '1' in e_flag:
                indices.append(i)
            if query_label == 'F' and '1' in f_flag:
                indices.append(i)
        
        self.tfrecords = [self.tfrecords[i] for i in indices]
        self.labels = [self.labels[i] for i in indices]
        self.records_intervals = [self.records_intervals[i] for i in indices]

        return self

    
    def to_text(self, output_path: str):
        '''
        Writes all tfrecords out to a text file
        :output_path: designated file output
        '''
        with open(output_path, 'w+') as f:
            for record in self.tfrecords:
                f.write(record + '\n')

    def to_wav(self, output_file):
        '''
        Outputs wav file based on the tfrecords within the query
        CAUTION: only use this for reasonable amounts of time, computation may take an absurd amount of time; storage is also a concern
        :output_path: designated file output
        '''
        res = []
        for record in self.tfrecords:
            example = parse_tfrecord(self.records_dir + record)
            audio = get_audio(example)
            res.append(audio)
        sound = np.hstack(res)
        wav_info = Audio(sound, rate=4000)
        with open(output_file, 'wb') as f:
            f.write(wav_info.data)


    def get_label_counts(self):
        '''
        Gets the count of labels in current query
        '''
        a_count = b_count = c_count = d_count = e_count = f_count = 0
        for label in self.labels:
            if '1' in label[0]:
                a_count += 1
            if '1' in label[1]:
                b_count += 1
            if '1' in label[2]:
                c_count += 1
            if '1' in label[3]:
                d_count += 1
            if '1' in label[4]:
                e_count += 1
            if '1' in label[5]:
                f_count += 1
        return [a_count, b_count, c_count, d_count, e_count, f_count]
    
    def count_ship_no_ship(self):
        '''
        Gets the counts of ship versus no ship (binary classification)
        '''
        ship_cnt = no_ship_cnt = 0
        for label in self.labels:
            if '1' in label[5]:
                no_ship_cnt += 1
            else:
                ship_cnt += 1
        return ship_cnt, no_ship_cnt
            
