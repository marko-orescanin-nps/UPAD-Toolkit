from src.constants import LABEL_COMBINATIONS
from utils.time_utils import nanos_to_ymd_str
from sklearn.preprocessing import MultiLabelBinarizer
import tensorflow as tf
import os
import pickle

def record_writer(path, audio, label_info, unique_id):
    '''
    Description: writes information into tfrecord format \n
    :path: directory to write the tfrecords to\n
    :audio: audio data to write for segment\n
    :label_info: contains information (ship_class, brg, rng, mmsi, desc) \n
    :unique_id: unique id for the segment (start and end timestamp)\n
    :returns: None\n
    '''

    # process the label_info into it's parts
    # desc = SHIP_DESIG
    label = []
    # A Features
    a_mmsi = []
    a_desc = []
    a_brg = []
    a_rng = []

    # B Features
    b_mmsi = []
    b_desc = []
    b_brg = []
    b_rng = []

    # C Features
    c_mmsi = []
    c_desc = []
    c_brg = []
    c_rng = []

    # D Features
    d_mmsi = []
    d_desc = []
    d_brg = []
    d_rng = []

    # E Features
    e_mmsi = []
    e_desc = []
    e_brg = []
    e_rng = []


    for info in label_info:
        ship_class, brg, rng, mmsi, desc = info
        if ship_class not in label and ship_class is not None:
            label.append(ship_class)
        if ship_class == 'Class A':
            a_brg.append(brg)
            a_rng.append(rng)
            a_mmsi.append(mmsi)
            a_desc.append(desc)
        if ship_class == 'Class B':
            b_brg.append(brg)
            b_rng.append(rng)
            b_mmsi.append(mmsi)
            b_desc.append(desc)
        if ship_class == 'Class C':
            c_brg.append(brg)
            c_rng.append(rng)
            c_mmsi.append(mmsi)
            c_desc.append(desc)
        if ship_class == 'Class D':
            d_brg.append(brg)
            d_rng.append(rng)
            d_mmsi.append(mmsi)
            d_desc.append(desc)
        if ship_class == 'Class E':
            e_brg.append(brg)
            e_rng.append(rng)
            e_mmsi.append(mmsi)
            e_desc.append(desc)

    if len(label) == 0:
        label = ['Class F']
        
    print(label)

    writer = tf.io.TFRecordWriter(path)

    audio_ser  = tf.io.serialize_tensor(audio).numpy()
    audio_feat = tf.train.Feature(bytes_list=tf.train.BytesList(value=[audio_ser]))

    a_brg_list = tf.train.FloatList(value = a_brg)
    a_brg_feat = tf.train.Feature(float_list = a_brg_list)

    a_rng_list = tf.train.FloatList(value = a_rng)
    a_rng_feat = tf.train.Feature(float_list = a_rng_list)

    a_mmsi_list = tf.train.Int64List(value = a_mmsi)
    a_mmsi_feat = tf.train.Feature(int64_list = a_mmsi_list)

    a_desc_list = tf.train.BytesList(value = a_desc)
    a_desc_feat = tf.train.Feature(bytes_list = a_desc_list)

    b_brg_list = tf.train.FloatList(value = b_brg)
    b_brg_feat = tf.train.Feature(float_list = b_brg_list)

    b_rng_list = tf.train.FloatList(value = b_rng)
    b_rng_feat = tf.train.Feature(float_list = b_rng_list)

    b_mmsi_list = tf.train.Int64List(value = b_mmsi)
    b_mmsi_feat = tf.train.Feature(int64_list = b_mmsi_list) 
    
    b_desc_list = tf.train.BytesList(value = b_desc)
    b_desc_feat = tf.train.Feature(bytes_list = b_desc_list)
    
    c_brg_list = tf.train.FloatList(value = c_brg)
    c_brg_feat = tf.train.Feature(float_list = c_brg_list)

    c_rng_list = tf.train.FloatList(value = c_rng)
    c_rng_feat = tf.train.Feature(float_list = c_rng_list)

    c_mmsi_list = tf.train.Int64List(value = c_mmsi)
    c_mmsi_feat = tf.train.Feature(int64_list = c_mmsi_list)
    
    c_desc_list = tf.train.BytesList(value = c_desc)
    c_desc_feat = tf.train.Feature(bytes_list = c_desc_list)
    
    d_brg_list = tf.train.FloatList(value = d_brg)
    d_brg_feat = tf.train.Feature(float_list = d_brg_list)

    d_rng_list = tf.train.FloatList(value = d_rng)
    d_rng_feat = tf.train.Feature(float_list = d_rng_list)

    d_mmsi_list = tf.train.Int64List(value = d_mmsi)
    d_mmsi_feat = tf.train.Feature(int64_list = d_mmsi_list)

    d_desc_list = tf.train.BytesList(value = d_desc)
    d_desc_feat = tf.train.Feature(bytes_list = d_desc_list)

    e_brg_list = tf.train.FloatList(value = e_brg)
    e_brg_feat = tf.train.Feature(float_list = e_brg_list)

    e_rng_list = tf.train.FloatList(value = e_rng)
    e_rng_feat = tf.train.Feature(float_list = e_rng_list)

    e_mmsi_list = tf.train.Int64List(value = e_mmsi)
    e_mmsi_feat = tf.train.Feature(int64_list = e_mmsi_list)

    e_desc_list = tf.train.BytesList(value = e_desc)
    e_desc_feat = tf.train.Feature(bytes_list = e_desc_list)

    enc = MultiLabelBinarizer().fit(LABEL_COMBINATIONS)
    vec = enc.transform([label])[0]
    label_list = tf.train.Int64List(value=[int(v) for v in vec])
    label_feat = tf.train.Feature(int64_list=label_list)

    unique_id = unique_id.encode('utf-8')
    unique_id_list = tf.train.BytesList(value = [unique_id])
    unique_id_feat = tf.train.Feature(bytes_list = unique_id_list)
    
    feature = {
        'audio': audio_feat,
        'label': label_feat,
        'a_brg'  : a_brg_feat,
        'a_rng'  : a_rng_feat,
        'a_mmsi' : a_mmsi_feat,
        'a_desc' : a_desc_feat,
        'b_brg'  : b_brg_feat,
        'b_rng'  : b_rng_feat, 
        'b_mmsi' : b_mmsi_feat,
        'b_desc' : b_desc_feat,
        'c_brg'  : c_brg_feat,
        'c_rng'  : c_rng_feat,
        'c_mmsi' : c_mmsi_feat,
        'c_desc' : c_desc_feat,
        'd_brg'  : d_brg_feat, 
        'd_rng'  : d_rng_feat,
        'd_mmsi' : d_mmsi_feat,
        'd_desc' : d_desc_feat,
        'e_brg'  : e_brg_feat,
        'e_rng'  : e_rng_feat,
        'e_mmsi' : e_mmsi_feat,
        'e_desc' : e_desc_feat,
        'unique_id' : unique_id_feat
    }

    example = tf.train.Example(features=tf.train.Features(feature=feature))
    writer.write(example.SerializeToString())
    writer.close()

def _parse_segment_function(example):
    '''
    Description: extracts information from tfrecord with a single sample

    :example: tfrecord
    '''
    feature_description = {
        'audio': tf.io.FixedLenFeature([], dtype=tf.string),
        'label': tf.io.FixedLenFeature([6], dtype=tf.int64),
        'a_brg': tf.io.RaggedFeature(tf.float32),
        'a_rng': tf.io.RaggedFeature(tf.float32),
        'a_mmsi': tf.io.RaggedFeature(tf.int64),
        'a_desc': tf.io.RaggedFeature(tf.string),
        'b_brg': tf.io.RaggedFeature(tf.float32),
        'b_rng': tf.io.RaggedFeature(tf.float32),
        'b_mmsi': tf.io.RaggedFeature(tf.int64),
        'b_desc': tf.io.RaggedFeature(tf.string),
        'c_brg': tf.io.RaggedFeature(tf.float32),
        'c_rng': tf.io.RaggedFeature(tf.float32),
        'c_mmsi': tf.io.RaggedFeature(tf.int64),
        'c_desc': tf.io.RaggedFeature(tf.string),
        'd_brg': tf.io.RaggedFeature(tf.float32),
        'd_rng': tf.io.RaggedFeature(tf.float32),
        'd_mmsi': tf.io.RaggedFeature(tf.int64),
        'd_desc': tf.io.RaggedFeature(tf.string),   
        'e_brg': tf.io.RaggedFeature(tf.float32),
        'e_rng': tf.io.RaggedFeature(tf.float32),
        'e_mmsi': tf.io.RaggedFeature(tf.int64),
        'e_desc': tf.io.RaggedFeature(tf.string), 
        'unique_id': tf.io.FixedLenFeature([], dtype=tf.string)  
    }
    return tf.io.parse_single_example(example, feature_description)

def parse_tfrecord(tfrecord_path: str):
    '''
    Description: Parses a single tfrecord

    :tfrecord_path: full path of tfrecord

    :returns: feature (dict)
    '''
    raw_dataset = tf.data.TFRecordDataset(tfrecord_path)
    example = raw_dataset.map(_parse_segment_function)
    for feature in example:
        return feature
    
def parse_group_tfrecord(tfrecord_path: str):
    '''
    Description: Parses a tfrecord with many samples

    :tfrecord_path: full path of tfrecord

    :returns: entire record (list of features)
    '''
    raw_dataset = tf.data.TFRecordDataset(tfrecord_path)
    example = raw_dataset.map(_parse_segment_function)
    return example

def get_audio(example):
    '''
    Description: take an example (parsed tfrecord) and extract the audio
    
    :example: feature taken from tfrecord

    :returns: numpy array with audio
    '''
    return tf.io.parse_tensor(example['audio'], out_type=tf.float32).numpy()

def translate_record_to_ymd(tfrecord_name: str):
    '''
    Description: takes in tfrecord and translates the interval to a ymd string tuple

    :tfrecord_name: full path of tfrecord

    :returns: tuple (ymd_str(start_nanos), ymd_str(end_nanos))
    '''
    start_nanos, end_nanos = translate_record_to_interval(tfrecord_name)
    return nanos_to_ymd_str(float(start_nanos)), nanos_to_ymd_str(float(end_nanos))

def translate_record_to_interval(tfrecord_name: str):
    '''
    Description: Grabs the interval from the name of the tfrecord

    :tfrecord_name: full path of tfrecord

    :returns: tuple (start_nanos, end_nanos)
    '''
    interval_str = tfrecord_name.split('.tfrecord')[0]
    start_nanos, end_nanos = interval_str.split('_')[:2] # grab the first two elements
    return float(start_nanos), float(end_nanos)

def translate_record_to_label(tfrecord_name: str):
    '''
    Description: Grabs the label from the name of the tfrecord

    :tfrecord_name: full path of tfrecord

    :returns: tuple containing all labels
    '''
    interval_str = tfrecord_name.split('.tfrecord')[0]
    a_label, b_label, c_label, d_label, e_label, f_label = interval_str.split('_')[2:]
    return a_label, b_label, c_label, d_label, e_label, f_label

def create_records_pickle(record_dir: str, output_pickle: str):
    '''
    Description: Tool for creating Lookup Table for Detect/Buffer split

    :record_dir: directory of detect/buffer containing tfrecords
    :output_pickle: output file for storing lookup table

    :returns: None
    '''
    result = []
    for record in sorted(os.listdir(record_dir)):
        result.append([translate_record_to_interval(record), translate_record_to_label(record)])
    with open(output_pickle, 'wb') as f:
        pickle.dump(result, f)
