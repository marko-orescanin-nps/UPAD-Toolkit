import random
import os
import argparse
import shutil
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from utils.split_utils import upsample, downsample


from passive_sonar_models.data.dataset_processor import AudioDataset

def decode_fn(record_bytes):
    feature_description = {
        'audio': tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'label': tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'a_brg'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'a_rng'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'a_mmsi' : tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'a_desc' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'b_brg'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'b_rng'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True), 
        'b_mmsi' : tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'b_desc' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'c_brg'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'c_rng'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'c_mmsi' : tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'c_desc' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'd_brg'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True), 
        'd_rng'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'd_mmsi' : tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'd_desc' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'e_brg'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'e_rng'  : tf.io.FixedLenSequenceFeature([], tf.float32, default_value=0.0, allow_missing=True),
        'e_mmsi' : tf.io.FixedLenSequenceFeature([], tf.int64, default_value=0, allow_missing=True),
        'e_desc' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True),
        'unique_id' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True)
    }
    return tf.io.parse_single_example(
        record_bytes,
        feature_description
    )

def audio_preprocess(dataset, counter, output_path, channels, process=False):

    ad = AudioDataset(channels=channels, filterDC=False) # turn off 500 Hz DC filter

    filename =  output_path + counter + '.tfrecord'
    if not os.path.exists(filename):
        f = open(filename,  'w+')
        f.close()

    writer = tf.io.TFRecordWriter(filename)

    for example in dataset.map(decode_fn):
        # parse the audio from the example in tfrecord
        audio = tf.io.parse_tensor(example['audio'][0], out_type=tf.float32)
        print(audio.numpy().shape)
        # change spectrogram based on num channels
        if process:
            print("preprocessing audio")
            if channels == 4:
                audio = ad.generate_multi_channel_mel(audio)
            elif channels == 1:
                audio = ad.generate_mel(audio)
            else:
                print("incorrect number of channels selected, use 1 or 4")
                break

        audio_ser  = tf.io.serialize_tensor(audio).numpy()
        audio_feat = tf.train.Feature(bytes_list=tf.train.BytesList(value=[audio_ser]))
        label_ser = tf.train.Int64List(value=example['label'].numpy())
        label_feat = tf.train.Feature(int64_list=label_ser)
        a_brg_list = tf.train.FloatList(value=example['a_brg'].numpy())
        a_brg_feat = tf.train.Feature(float_list = a_brg_list)
        a_rng_list = tf.train.FloatList(value=example['a_rng'].numpy())
        a_rng_feat = tf.train.Feature(float_list = a_rng_list)
        a_mmsi_list = tf.train.Int64List(value=example['a_mmsi'].numpy())
        a_mmsi_feat = tf.train.Feature(int64_list = a_mmsi_list)
        a_desc_list = tf.train.BytesList(value=example['a_desc'].numpy())
        a_desc_feat = tf.train.Feature(bytes_list = a_desc_list)
        b_brg_list = tf.train.FloatList(value=example['b_brg'].numpy())
        b_brg_feat = tf.train.Feature(float_list = b_brg_list)
        b_rng_list = tf.train.FloatList(value=example['b_rng'].numpy())
        b_rng_feat = tf.train.Feature(float_list = b_rng_list)
        b_mmsi_list = tf.train.Int64List(value=example['b_mmsi'].numpy())
        b_mmsi_feat = tf.train.Feature(int64_list = b_mmsi_list) 
        b_desc_list = tf.train.BytesList(value=example['b_desc'].numpy())
        b_desc_feat = tf.train.Feature(bytes_list = b_desc_list)
        c_brg_list = tf.train.FloatList(value=example['c_brg'].numpy())
        c_brg_feat = tf.train.Feature(float_list = c_brg_list)
        c_rng_list = tf.train.FloatList(value=example['c_rng'].numpy())
        c_rng_feat = tf.train.Feature(float_list = c_rng_list)
        c_mmsi_list = tf.train.Int64List(value=example['c_mmsi'].numpy())
        c_mmsi_feat = tf.train.Feature(int64_list = c_mmsi_list)
        c_desc_list = tf.train.BytesList(value=example['c_desc'].numpy())
        c_desc_feat = tf.train.Feature(bytes_list = c_desc_list)
        d_brg_list = tf.train.FloatList(value=example['d_brg'].numpy())
        d_brg_feat = tf.train.Feature(float_list = d_brg_list)  
        d_rng_list = tf.train.FloatList(value=example['d_rng'].numpy())
        d_rng_feat = tf.train.Feature(float_list = d_rng_list)
        d_mmsi_list = tf.train.Int64List(value=example['d_mmsi'].numpy())
        d_mmsi_feat = tf.train.Feature(int64_list = d_mmsi_list)
        d_desc_list = tf.train.BytesList(value=example['d_desc'].numpy())
        d_desc_feat = tf.train.Feature(bytes_list = d_desc_list)
        e_brg_list = tf.train.FloatList(value=example['e_brg'].numpy())
        e_brg_feat = tf.train.Feature(float_list = e_brg_list)
        e_rng_list = tf.train.FloatList(value=example['e_rng'].numpy())
        e_rng_feat = tf.train.Feature(float_list = e_rng_list)
        e_mmsi_list = tf.train.Int64List(value=example['e_mmsi'].numpy())
        e_mmsi_feat = tf.train.Feature(int64_list = e_mmsi_list)
        e_desc_list = tf.train.BytesList(value=example['e_desc'].numpy())
        e_desc_feat = tf.train.Feature(bytes_list = e_desc_list)

        unique_id_list = tf.train.BytesList(value=example['unique_id'].numpy())
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
        new_example = tf.train.Example(features=tf.train.Features(feature=feature))
        writer.write(new_example.SerializeToString())
        
    writer.close()

def process(files_segment, counter, output_path, num_channels, should_preprocess=False):
    '''
    process a segment of tfrecord lines and return a single tfrecord
    '''
    # create dataset from files
    
    dataset = tf.data.TFRecordDataset(files_segment)
    
    # PREPROCESSING
    audio_preprocess(dataset, counter, output_path, num_channels, should_preprocess)



if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--records_dir", required=True)
    ap.add_argument("--split_dir", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--section", required=True)
    ap.add_argument("--downsample", required=True)
    ap.add_argument("--upsample", required=True)
    ap.add_argument("--num_channels", required=True)
    ap.add_argument("--audio_preprocess", default=False)

    args = vars(ap.parse_args())

    records_dir = args['records_dir']
    split_dir = args['split_dir']
    output_dir = args['output_dir']
    section = args['section']
    downsample_factor = int(args['downsample'])
    upsample_factor = int(args['upsample'])
    num_channels = int(args['num_channels'])
    should_preprocess = bool(args['audio_preprocess'])

    if not os.path.exists(output_dir):
        print("path did not exist")
        os.makedirs(output_dir)
    
    # copy split file into new output_directory
    shutil.copyfile(split_dir + section + '.txt', output_dir + section + '.txt')
    if upsample_factor > 0:
        upsample(output_dir + section + '.txt', output_dir + section + '.txt', upsample_factor) 
    if downsample_factor > 0:
        downsample(output_dir + section + '.txt', output_dir + section + '.txt', downsample_factor)
    # work on the split
    with open(output_dir + section + '.txt', 'r') as f:
        lines = [line.rstrip('\n') for line in f]
        # shuffle the lines before splitting into segments
        random.shuffle(lines)
        lines = [records_dir + line for line in lines]
        # create 128 long segments from the lines and concatenate them.
        counter = 1
        i = 0
        while i < len(lines):
            if i + 128 > len(lines):
                new_record = process(lines[i:], section + '_' + str(counter), output_dir, num_channels, should_preprocess=should_preprocess)
            else:
                new_record = process(lines[i:i+128], section + '_' + str(counter), output_dir, num_channels, should_preprocess=should_preprocess)
            i += 128
            counter += 1

    # fill the new split txt file with modified names
    with open(output_dir + section + '.txt', 'w+') as f:
        for filename in sorted(os.listdir(output_dir)):
            if '.tfrecord' in filename:
                f.write(filename + '\n')
        

