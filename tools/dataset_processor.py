"""
    Author: John Fischer
    Passive Sonar

    Module for processing audio samples into appropriate input features given input params.

"""

import os
from types import ModuleType
import numpy as np
import tensorflow as tf
from math import ceil
from pathlib import Path
import glob
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MultiLabelBinarizer

class AudioDataset(object):

    def __init__(self,
                    win_size=256,
                    overlap=50,
                    sample_points=1024,
                    sample_rate=4000,
                    duration=30,
                    channels=1,
                    min_freq=0,
                    max_freq=2000,
                    custom_pad=False,
                    filterDC=True,
                    mel_bins=128,
                    data_filepath=None,
                    batch_size=256,
                    epochs=400,
                    augment=False,
                    by_channel_aug=False,
                    modelType = "multi_class",
                    mode='train',
                    type_dataset='train',
                    num_classes=5,
                    class_weight=False):

                    self.class_weight = class_weight
                    self.num_classes = num_classes
                    self.class_count=[]
                    self.data_filepath=data_filepath
                    self.batch_size=batch_size
                    self.epochs=epochs
                    self.augment = augment
                    self.by_channel_augment = by_channel_aug
                    self.duration = duration
                    self.mode = mode
                    self.type_dataset=type_dataset
                    self.model_type = modelType
                    self.filepaths = []
                    self.custom_pad = custom_pad
                    self.filterDC = filterDC
                    self.channels=channels
                    self.SAMPLE_RATE = sample_rate
                    self.min_freq = min_freq
                    self.max_freq = max_freq
                    self.input_shape = (channels, sample_rate*duration)
                    
                    #Calculations required for STFT, spectrogram generation, and model input
                    self.WIN_SIZE = (int)((win_size * .001) * self.SAMPLE_RATE)
                    
                    #Calculate number of samples to step based on overlap percentage
                    self.OVERLAP = overlap
                    self.STEP = (int)(self.WIN_SIZE-((self.OVERLAP / 100) * self.WIN_SIZE))

                    #FFT_Length in samples
                    self.SAMPLE_POINTS = sample_points

                    self.MEL_BINS = mel_bins
                    self.STFT_BINS = (self.SAMPLE_POINTS // 2) + 1

                    if self.min_freq == 0:
                        self.LOWER_BOUND = 0
                        self.BIN_LOW = 0
                    else:
                        self.BIN_LOW = self.get_bin_index(min_freq)
                        self.LOWER_BOUND = (self.BIN_LOW * self.SAMPLE_RATE) // self.SAMPLE_POINTS
                    if self.max_freq == 2000:
                        self.UPPER_BOUND = self.SAMPLE_RATE / 2
                        self.BIN_HIGH = self.STFT_BINS-1
                    else:
                        self.BIN_HIGH = self.get_bin_index(max_freq)
                        self.UPPER_BOUND = ceil((self.BIN_HIGH * self.SAMPLE_RATE) / self.SAMPLE_POINTS)

                    self.TIME_SPACE = ceil((self.duration * self.SAMPLE_RATE) / self.STEP)

                    if self.filterDC:
                        self.NUM_SPEC_BINS = self.BIN_HIGH - self.BIN_LOW - 36
                    else:
                        self.NUM_SPEC_BINS = self.BIN_HIGH - self.BIN_LOW + 1


    """
        Getter functions to return true labels array and filepaths array
        These functions are used during prediction with the saved model
    """
    
    def get_filepaths(self):
        return self.filepaths

    def get_class_count(self):
        if self.model_type == "binary":
            return np.array([self.class_count[-1]])
        else:                
            return self.class_count

    def make_dataset(self, input_file, generator_type):
        """
        create the actual dataset
        The dataset consists of spectrogram images and a metadata file with the labels
        This is required to support multiple labels per image
        
        #Arguments
            .txt: file located in splits_filepath in object constructor the contains a list of .tfrecords files
            generator: either 'stft' or 'mel-log' for which output to transform audio files into

        #Returns
            dataset: tensorflow dataset object of spectrograms and lables
            size: size of dataset, gets around some tensorflow eager execution to get know dataset size from length in .txt file
        """
        
        def parse_tfrecord(example):
            if self.model_type == "multi_class":
                feature_description = {
                    'audio': tf.io.FixedLenFeature([], dtype=tf.string),
                    'label': tf.io.FixedLenFeature([5], dtype=tf.int64),
                    'brg'  : tf.io.FixedLenFeature([1], dtype=tf.float32),
                    'rng'  : tf.io.FixedLenFeature([1], dtype=tf.float32),
                }
            elif self.model_type in ["multi_label","binary"]:
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
                    'unique_id' : tf.io.FixedLenSequenceFeature([], tf.string, default_value='', allow_missing=True)
                }

            example = tf.io.parse_single_example(example, feature_description)

            return example

        def prepare_samples(example):
            if self.model_type == "multi_class":
                audio = tf.io.parse_tensor(example['audio'], out_type=tf.float32)
            elif self.model_type in ["multi_label","binary"]:
                audio = tf.io.parse_tensor(example['audio'][0], out_type=tf.float32)
            
            label = example['label']

            if self.model_type == "binary":
                if label[-1] == 0:
                    label = 1
                else:
                    label = 0
                       
            if generator_type == 'stft':
                audio = self.generate_stft(audio)
            elif generator_type == 'multi_channel_stft':
                audio = self.generate_multi_channel_stft(audio)
            elif generator_type == 'mel-log':
                audio = self.generate_mel(audio)
            elif generator_type == 'multi_channel_mel-log':
                audio = self.generate_multi_channel_mel(audio)
            
            return audio, label
        
        def generate_class_count(dataset):
            class_count = np.zeros(self.num_classes,dtype=int)
            for element in dataset.as_numpy_iterator():
                label = element['label']
                if self.model_type == 'binary':
                    if label[-1] == 0:
                        class_count += 1
                else:
                    class_count += label
            
            return class_count
        
        with open(input_file) as f:
            filenames = f.readlines()
        self.filepaths = [os.path.join(self.data_filepath, str.strip(filename)) for filename in filenames]
        self.buffer_size = len(self.filepaths)

              
        if(self.type_dataset in ['train','val']):
            filename_dataset = (tf.data.Dataset.from_tensor_slices(self.filepaths)
                .shuffle(self.buffer_size))    

            dataset = (tf.data.TFRecordDataset(filename_dataset, num_parallel_reads=tf.data.AUTOTUNE)
                .map(parse_tfrecord, num_parallel_calls=tf.data.AUTOTUNE))

            if (self.class_weight and self.type_dataset=='train'):
                self.class_count = generate_class_count(dataset)

            dataset = dataset.map(prepare_samples, num_parallel_calls=tf.data.AUTOTUNE)
                                
            if self.type_dataset == 'train':
                #dataset = dataset.cache()
                dataset = dataset.shuffle(self.batch_size*3)
                if self.augment:
                    if self.by_channel_augment:
                        dataset = dataset.map(lambda x,y: tf.cond(tf.random.uniform([],0,1) > .75, lambda: self.variable_channel_freq_mask(x,y,10), lambda: (x,y)), num_parallel_calls=tf.data.AUTOTUNE)
                        dataset = dataset.map(lambda x,y: tf.cond(tf.random.uniform([],0,1) > .75, lambda: self.variable_channel_time_mask(x,y,15), lambda: (x,y)), num_parallel_calls=tf.data.AUTOTUNE)
                    else:
                        dataset = dataset.map(lambda x,y: tf.cond(tf.random.uniform([],0,1) > .75, lambda: self.freq_mask(x,y,10), lambda: (x,y)), num_parallel_calls=tf.data.AUTOTUNE)
                        dataset = dataset.map(lambda x,y: tf.cond(tf.random.uniform([],0,1) > .75, lambda: self.time_mask(x,y,15), lambda: (x,y)), num_parallel_calls=tf.data.AUTOTUNE)

            #dataset = dataset.repeat(self.epochs) 
            dataset = dataset.batch(self.batch_size, drop_remainder=True)                
            dataset = dataset.prefetch(tf.data.AUTOTUNE)                        
        
        else:
            dataset = (tf.data.TFRecordDataset(self.filepaths, num_parallel_reads=tf.data.AUTOTUNE)
                .map(parse_tfrecord, num_parallel_calls=tf.data.AUTOTUNE))
        
            dataset = (dataset.map(prepare_samples, num_parallel_calls=tf.data.AUTOTUNE)
                .cache()
                .batch(self.batch_size)
                .prefetch(tf.data.AUTOTUNE))               
                
        if (self.class_weight and self.type_dataset == 'train'):
            return dataset, len(self.filepaths), self.get_class_count()
        else:
            return dataset, len(self.filepaths), None
        
        
        
    #Function takes in a flat audio sample and returns a log-scale (db) amplitude-only Short Time Fourier Transform with a single channel
    def generate_stft(self, audio):
                
        # tf.squeeze(audio) to change shape to just samples, removes number of channels
        if(tf.rank(audio) == 2):
            pressure_channel = audio[0]
            audio_squeeze = tf.reshape(tf.squeeze(pressure_channel), [1, -1])
        else:
            audio_squeeze = tf.reshape(tf.squeeze(audio), [1, -1])

        #Pad audio to mitigate effects on end of sample
        if self.custom_pad == True:
            audio_squeeze = self.pad_audio_extend_last_sample(audio_squeeze)

        stfts = tf.signal.stft(audio_squeeze, frame_length=self.WIN_SIZE, frame_step=self.STEP, fft_length=self.SAMPLE_POINTS, window_fn=tf.signal.hann_window, pad_end=True )

        #Remove padding from stfts to get expected time_space
        if self.custom_pad == True:
            stfts = self.remove_padding(stfts)

        mag_spec_base = tf.abs(stfts)

        if self.filterDC:
            mag_spec_base = tf.concat([mag_spec_base[:, :, self.BIN_LOW:110], mag_spec_base[:, :, 147:]], 2)
        else:
            #Filter out unwanted frequencies
            mag_spec_base = mag_spec_base[:,:,self.BIN_LOW:self.BIN_HIGH + 1]

        #Convert Spectrograms to db scale
        log_spectrograms = 20 * tf.math.log(mag_spec_base/tf.math.reduce_max(mag_spec_base) + 1e-6)/2.303

        log_spectrograms = tf.math.maximum(log_spectrograms,tf.math.reduce_max(log_spectrograms)-80)

        # stft function returns channels, time, freq, need to convert to time, freq, channels for CNNs
        final_spec =  tf.reshape(tf.squeeze(log_spectrograms), [self.TIME_SPACE, self.NUM_SPEC_BINS, 1])
        
        return final_spec


    #Function takes in a flat audio sample and returns a log-scale (db) amplitude-only Short Time Fourier Transform with either 2 
    #(vertical velocity, pressure) or 4 (3D velocity, pressure) channels.
    def generate_multi_channel_stft(self, audio):
        
        channels = tf.split(audio, num_or_size_splits=4, axis=0) 
        
        all_channels = []
        
        for ch in channels:
            audio_squeeze = tf.reshape(tf.squeeze(ch), [1,-1])

            if self.custom_pad == True:
                audio_squeeze = self.pad_audio_extend_last_sample(audio_squeeze)

            stfts = tf.signal.stft(audio_squeeze, frame_length=self.WIN_SIZE, frame_step=self.STEP, fft_length=self.SAMPLE_POINTS, window_fn=tf.signal.hann_window, pad_end=True )

            if self.custom_pad == True:
                stfts = self.remove_padding(stfts)

            mag_spec_base = tf.abs(stfts)

            if self.filterDC:
                mag_spec_base = tf.concat([mag_spec_base[:, :, self.BIN_LOW:110], mag_spec_base[:, :, 147:]], 2)
            else:
                # Filter out unwanted frequencies
                mag_spec_base = mag_spec_base[:, :, self.BIN_LOW:self.BIN_HIGH + 1]

            # built in tf.math.log is log base 2, need log base 10
            log_spectrograms = 20 * tf.math.log(mag_spec_base/tf.math.reduce_max(mag_spec_base) + 1e-6)/2.303

            log_spectrograms = tf.math.maximum(log_spectrograms,tf.math.reduce_max(log_spectrograms)-80)

            all_channels.append(tf.squeeze(log_spectrograms))
        
        # function returns channels, time, freq, need to convert to time, freq, channels for CNNs
        if self.channels == 2:
            final_stft = tf.stack([all_channels[0], all_channels[3]], axis=2)
        else:
            final_stft =  tf.stack([all_channels[0], all_channels[1], all_channels[2], all_channels[3]], axis=2)

        return final_stft
    

    #Function takes in a flat audio sample and returns a log mel scale spectrogram with a single channel 
    def generate_mel(self, audio):
        
        # For audio data from a multi-channel source, audio has shape [num_channels, samples], for single-channel, audio has shape [num_samples]
        if(tf.rank(audio) == 2):
            pressure_channel = audio[0]
            audio_squeeze = tf.reshape(tf.squeeze(pressure_channel), [1, -1])
        else:
            audio_squeeze = tf.reshape(tf.squeeze(audio), [1, -1])

        # Pad audio to mitigate effects on end of sample
        if self.custom_pad == True:
            audio_squeeze = self.pad_audio_extend_last_sample(audio_squeeze)

        stfts = tf.signal.stft(audio_squeeze, frame_length=self.WIN_SIZE, frame_step=self.STEP,
                               fft_length=self.SAMPLE_POINTS, window_fn=tf.signal.hann_window, pad_end=True)

        # Remove padding from stfts to get expected time_space
        if self.custom_pad == True:
            stfts = self.remove_padding(stfts)

        mag_spec_base = tf.abs(stfts)

        if self.filterDC:
            mag_spec_base = tf.concat([mag_spec_base[:, :, self.BIN_LOW:110], mag_spec_base[:, :, 147:]], 2)
        else:
            #Filter out unwanted frequencies
            mag_spec_base = mag_spec_base[:,:,self.BIN_LOW:self.BIN_HIGH + 1]

        linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(self.MEL_BINS, self.NUM_SPEC_BINS, self.SAMPLE_RATE, self.LOWER_BOUND, self.UPPER_BOUND)
        mel_spectrograms = tf.tensordot(mag_spec_base, linear_to_mel_weight_matrix, 1)

        # Compute a stabilized log to get log-magnitude mel-scale spectrograms.
        log_mel_spectrograms = 20 * tf.math.log(mel_spectrograms/tf.math.reduce_max(mel_spectrograms) + 1e-6)/2.303

        log_mel_spectrograms = tf.math.maximum(log_mel_spectrograms,tf.math.reduce_max(log_mel_spectrograms)-80)

        # mfcc function returns channels, time, freq, need to convert to time, freq, channels for CNNs
        final_mfcc =  tf.reshape(tf.squeeze(log_mel_spectrograms), [self.TIME_SPACE, self.MEL_BINS, 1])
        
        return final_mfcc


    #Function takes in a flat audio sample and returns a log mel scale spectrogram with either 2 
    #(vertical velocity, pressure) or 4 (3D velocity, pressure) channels.
    def generate_multi_channel_mel(self, audio):
                 
        channels = tf.split(audio, num_or_size_splits=4, axis=0)

        all_channels = []

        for ch in channels:
            # tf.squeeze(audio) to change shape to just samples, removes number of channels
            audio_squeeze = tf.reshape(tf.squeeze(ch), [1,-1])

            if self.custom_pad == True:
                audio_squeeze = self.pad_audio_extend_last_sample(audio_squeeze)

            stfts = tf.signal.stft(audio_squeeze, frame_length=self.WIN_SIZE, frame_step=self.STEP, fft_length=self.SAMPLE_POINTS, window_fn=tf.signal.hann_window, pad_end=True )

            if self.custom_pad == True:
                stfts = self.remove_padding(stfts)

            mag_spec_base = tf.abs(stfts)

            if self.filterDC:
                mag_spec_base = tf.concat([mag_spec_base[:, :, self.BIN_LOW:110], mag_spec_base[:, :, 147:]], 2)
            else:
                # Filter out unwanted frequencies
                mag_spec_base = mag_spec_base[:, :, self.BIN_LOW:self.BIN_HIGH + 1]

            linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(self.MEL_BINS, self.NUM_SPEC_BINS, self.SAMPLE_RATE, self.LOWER_BOUND, self.UPPER_BOUND)
            mel_spectrograms = tf.tensordot(mag_spec_base, linear_to_mel_weight_matrix, 1)

            # Compute a stabilized log to get log-magnitude mel-scale spectrograms.
            log_mel_spectrograms = 20 * tf.math.log(mel_spectrograms/tf.math.reduce_max(mel_spectrograms) + 1e-6)/2.303

            log_mel_spectrograms = tf.math.maximum(log_mel_spectrograms,tf.math.reduce_max(log_mel_spectrograms)-80)

            all_channels.append(tf.squeeze(log_mel_spectrograms))

        # mfcc function returns channels, time, freq, need to convert to time, freq, channels for CNNs
        if self.channels == 2:
            final_mfcc = tf.stack([all_channels[0],all_channels[3]], axis=2)
        else:
            final_mfcc =  tf.stack([all_channels[0], all_channels[1], all_channels[2], all_channels[3]], axis=2)

        return final_mfcc
    
    
    
    #Return STFT frequency bin associated with frequency parameter
    def get_bin_index(self, frequency):
        bin = ceil((frequency*self.SAMPLE_POINTS) / self.SAMPLE_RATE)
        return bin

    #Remove padding from STFT to return the correct length STFT
    def remove_padding(self, STFT):
        return STFT[:,0:self.TIME_SPACE,:]

    #Pad audio by repeating last FFT Frame to mitigate edge effects at end of sample
    def pad_audio_repeat_last_frame(self, audio):
        last_frame = audio[:, -self.SAMPLE_POINTS:-1]
        return tf.concat([audio, last_frame], axis=1)

    #Pad audio by reflecting last audio sample for FFT Frame length
    def pad_audio_reflect_last_sample(self, audio):
        paddings = tf.constant([[0,0], [0,self.SAMPLE_POINTS]])
        pad_val = tf.reverse(audio[0,-1], axis=1)
        return tf.pad(audio, paddings=paddings, mode='CONSTANT', constant_values=pad_val)

    #Pad audio by extending the last sample
    def pad_audio_extend_last_sample(self, audio):
        paddings = tf.constant([[0, 0], [0, self.SAMPLE_POINTS]])
        pad_val = audio[0, -1]
        return tf.pad(audio, paddings=paddings, mode='CONSTANT', constant_values=pad_val)
    
    '''
        Adapted from Tensorflow IO Codebase to work for multi-channel audio
        Args:
            audio:  Spectrogram in format (time,freq, channels)
            mask_param:  maximum number of freq / mel bands to filter.  
        Returns:
            aug_audio: Spectrogram with the same number of channels each channel with the same freq mask applied.
    '''
    def freq_mask(self,audio,label,mask_param):
        #Put audio in (channels,time,freq) format for manipulation
        input_chan_first = tf.transpose(audio, perm=[2,0,1])
        
        audio_shape = tf.shape(input_chan_first) 

        #split audio by channel to apply augmentation
        channels = tf.split(input_chan_first, num_or_size_splits=self.channels,axis=0)
    
        #List to hold output
        output = []
    
        #Index of the highest frequency channel
        freq_max = audio_shape[2]

        #Random parameters for masking.  Frequencies between f0 and f0+f will be masked
        f = tf.random.uniform(shape=(), minval=0, maxval=mask_param, dtype=tf.dtypes.int32)
        f0 = tf.random.uniform(shape=(), minval=0, maxval=freq_max - f, dtype=tf.dtypes.int32)

        indices = tf.reshape(tf.range(freq_max), (1, -1))
        condition = tf.math.logical_and(tf.math.greater_equal(indices, f0), tf.math.less(indices, f0 + f))

        for ch in channels:
            output.append(tf.where(condition, tf.cast(0, input_chan_first.dtype), ch[0]))
            
        
        return (tf.stack(output,axis=2),label)

    '''
        Adapted from Tensorflow IO Codebase to work for multi-channel audio
        Args:
            audio:  Spectrogram in format (time,freq, channels)
            mask_param:  maximum number of freq / mel bands to filter.  
        Returns:
            aug_audio: Spectrogram with the same number of channels each channel with a unique freq mask applied.
    '''
    def variable_channel_freq_mask(self,audio,label,mask_param):
        #Put audio in (channels,time,freq) format for manipulation
        input_chan_first = tf.transpose(audio, perm=[2,0,1])
        
        audio_shape = tf.shape(input_chan_first) 

        #split audio by channel to apply augmentation
        channels = tf.split(input_chan_first, num_or_size_splits=self.channels,axis=0)
    
        #List to hold output
        output = []
    
        #Index of the highest frequency channel
        freq_max = audio_shape[2]

        for ch in channels:
            #Random parameters for masking.  Frequencies between f0 and f0+f will be masked
            f = tf.random.uniform(shape=(), minval=0, maxval=mask_param, dtype=tf.dtypes.int32)
            f0 = tf.random.uniform(shape=(), minval=0, maxval=freq_max - f, dtype=tf.dtypes.int32)

            indices = tf.reshape(tf.range(freq_max), (1, -1))
            condition = tf.math.logical_and(tf.math.greater_equal(indices, f0), tf.math.less(indices, f0 + f))
            
            output.append(tf.where(condition, tf.cast(0, input_chan_first.dtype), ch[0]))
            
        
        return (tf.stack(output,axis=2),label)



    '''
        Adapted from Tensorflow IO Codebase to work for multi-channel audio
        Args:
            audio:  Spectrogram in format (time,freq, channels)
            mask_param:  maximum number of time bands to filter.  
        Returns:
            aug_audio: Spectrogram with the same number of channels each channel with the same time mask applied.
    '''
    def time_mask(self,audio,label,mask_param):
        #Put audio in (channels,time,freq) format for manipulation
        input_chan_first = tf.transpose(audio, perm=[2,0,1])
        
        audio_shape = tf.shape(input_chan_first) 

        #split audio by channel to apply augmentation
        channels = tf.split(input_chan_first, num_or_size_splits=self.channels,axis=0)
        
        #List to hold output
        output = []
    
        #Index of the highest time channel
        time_max = audio_shape[1]

        #Random parameters for masking.  Frequencies between f0 and f0+f will be masked
        t = tf.random.uniform(shape=(), minval=0, maxval=mask_param, dtype=tf.dtypes.int32)
        t0 = tf.random.uniform(shape=(), minval=0, maxval=time_max - t, dtype=tf.dtypes.int32)

        indices = tf.reshape(tf.range(time_max), (-1, 1))
        condition = tf.math.logical_and(tf.math.greater_equal(indices, t0), tf.math.less(indices, t0 + t))

        for ch in channels:
            output.append(tf.where(condition, tf.cast(0, input_chan_first.dtype), ch[0]))
            
        
        return (tf.stack(output,axis=2),label)

    '''
        Adapted from Tensorflow IO Codebase to work for multi-channel audio.
        Args:
            audio:  Spectrogram in format (time,freq, channels)
            mask_param:  maximum number of time bands to filter.  
        Returns:
            aug_audio: Spectrogram with the same number of channels each channel with a unique time mask applied.
    '''
    def variable_channel_time_mask(self,audio,label,mask_param):
        #Put audio in (channels,time,freq) format for manipulation
        input_chan_first = tf.transpose(audio, perm=[2,0,1])
        
        audio_shape = tf.shape(input_chan_first) 

        #split audio by channel to apply augmentation
        channels = tf.split(input_chan_first, num_or_size_splits=self.channels,axis=0)
    
        #List to hold output
        output = []
    
        #Index of the highest time channel
        time_max = audio_shape[1]

        for ch in channels:
            #Random parameters for masking.  Frequencies between f0 and f0+f will be masked
            t = tf.random.uniform(shape=(), minval=0, maxval=mask_param, dtype=tf.dtypes.int32)
            t0 = tf.random.uniform(shape=(), minval=0, maxval=time_max - t, dtype=tf.dtypes.int32)

            indices = tf.reshape(tf.range(time_max), (-1, 1))
            condition = tf.math.logical_and(tf.math.greater_equal(indices, t0), tf.math.less(indices, t0 + t))

            output.append(tf.where(condition, tf.cast(0, input_chan_first.dtype), ch[0]))
            
        
        return (tf.stack(output,axis=2),label)

    def random_channel_mask(self, audio, label):
        #Put audio in (channels,time,freq) format for manipulation
        input_chan_first = tf.transpose(audio, perm=[2,0,1])       
    
        channel_to_mask = tf.random.uniform(shape=(), minval=0, maxval=self.channels, dtype=tf.dtypes.int32)
        
        zero_channel = tf.zeros_like(input_chan_first[0], dtype=input_chan_first.dtype)

        indices = tf.reshape(tf.range(self.channels), (-1, 1))

        indices = tf.expand_dims(indices,axis=2)

        

        channels_out = tf.where(condition, zero_channel, input_chan_first)
        
        return (tf.transpose(channels_out,perm=[1,2,0]),label)