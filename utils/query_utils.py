# provide information and statistics on a query dataframe

import numpy as np
import pandas as pd


def get_individual_label_counts(df: pd.DataFrame):
    a_count = df.query('a_label == 1')['a_label'].count()
    b_count = df.query('b_label == 1')['b_label'].count()
    c_count = df.query('c_label == 1')['c_label'].count()
    d_count = df.query('d_label == 1')['d_label'].count()
    e_count = df.query('e_label == 1')['e_label'].count()
    return [a_count, b_count, c_count, d_count, e_count]

def get_label_counts(df: pd.DataFrame, normalize=False) -> pd.Series:
    return df[['a_label', 'b_label', 'c_label', 'd_label', 'e_label']].value_counts(normalize=normalize)

def plot_label_counts(df: pd.DataFrame, normalize=False):
    ax = get_label_counts(df, normalize).plot.barh()
    _ = ax.set_xlabel('Label Combos') 
    _ = ax.set_ylabel('Frequency')

def get_individual_mmsi_counts(df: pd.DataFrame) -> dict:
    unique_mmsis = {}
    for _, row in df.iterrows():
        mmsi_list = row['mmsi_list']
        for mmsi in mmsi_list:
            if mmsi not in unique_mmsis:
                unique_mmsis[mmsi] = 1
            else:
                unique_mmsis[mmsi] += 1
    return unique_mmsis

def get_mmsi_counts(df: pd.DataFrame, normalize=False) -> pd.Series:
    df = combine_mmsis(df)
    return df['mmsi_list'].value_counts(normalize=normalize)



def plot_mmsi_counts(df: pd.DataFrame, normalize=False):
    ax = get_mmsi_counts(df, normalize).plot.barh()
    _ = ax.set_xlabel('MMSIs') 
    _ = ax.set_ylabel('Frequency') 

def get_individual_desc_counts(df: pd.DataFrame) -> dict:
    unique_descs = {}
    for _, row in df.iterrows():
        desc_list = row['desc_list']
        for desc in desc_list:
            if desc not in unique_descs:
                unique_descs[desc] = 1
            else:
                unique_descs[desc] += 1
    
    return unique_descs


def get_desc_counts(df: pd.DataFrame, normalize=False) -> pd.Series:
    df = combine_desc(df)
    return df['desc_list'].value_counts(normalize=normalize)



def plot_desc_counts(df: pd.DataFrame, normalize=False):
    ax = get_desc_counts(df, normalize).plot.barh()
    _ = ax.set_xlabel('Descriptions') 
    _ = ax.set_ylabel('Frequency') 


def downsample_e(df: pd.DataFrame, method: str = 'max') -> pd.DataFrame:
    '''
    df: dataframe of query information
    method: max or mean
    '''

    count_list = get_individual_label_counts(df)[:-1]
    
    if sum(count_list) == 0:
        return df

    method_value = max(count_list) if method == 'max' else np.int64(np.mean(count_list))
    e_samples = df.query('e_label == 1').sample(n=method_value)
    df = df.query('e_label == 0')
    return pd.concat([df, e_samples])


def labeled_mmsi(df, label, column_name):
    new_list = []
    for _, item in df[column_name].iteritems():
        new_list.append([label + ': ' + str(mmsi) for mmsi in item])
    return pd.Series(new_list)

def combine_mmsis(df: pd.DataFrame):
    # label all the mmsis
    df['labeled_a_mmsi'] = labeled_mmsi(df, 'A', 'a_mmsi')
    df['labeled_b_mmsi'] = labeled_mmsi(df, 'B', 'b_mmsi')
    df['labeled_c_mmsi'] = labeled_mmsi(df, 'C', 'c_mmsi')
    df['labeled_d_mmsi'] = labeled_mmsi(df, 'D', 'd_mmsi')

    # combine all mmsis into one column
    df['mmsi_list'] = df['labeled_a_mmsi'] + \
                      df['labeled_b_mmsi'] + \
                      df['labeled_c_mmsi'] + \
                      df['labeled_d_mmsi'] 
    return df

def labeled_desc(df, label, column_name):
    new_list = []
    for _, item in df[column_name].iteritems():
        new_list.append([label + ': ' + desc.decode() for desc in item])
    return pd.Series(new_list) 

def combine_desc(df: pd.DataFrame):
    df['labeled_a_desc'] = labeled_desc(df, 'A', 'a_desc')
    df['labeled_b_desc'] = labeled_desc(df, 'B', 'b_desc')
    df['labeled_c_desc'] = labeled_desc(df, 'C', 'c_desc')
    df['labeled_d_desc'] = labeled_desc(df, 'D', 'd_desc')

    df['desc_list'] = df['labeled_a_desc'] + \
                      df['labeled_b_desc'] + \
                      df['labeled_c_desc'] + \
                      df['labeled_d_desc']  
    return df

def start_end_times(df: pd.DataFrame):
    new = df['unique_id'].str.decode('utf-8').str.split('_', n=2, expand=True)
    df['start_time'] = new[0]
    df['end_time'] = new[1]
    return df
