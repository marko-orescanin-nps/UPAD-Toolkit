import pandas as pd
import librosa
import numpy as np
import glob
import os
import sys

from utils.time_utils import wav_path_to_nanos

def load_wav(f, sample_rate, mono):
    '''
    Description: loads wav file
    :f: file to load
    :sample_rate: sample rate of the audio
    :mono: boolean, True if not multi-channel audio
    '''
    y, _ = librosa.load(f, sr=sample_rate, mono=mono)
    y = np.reshape(y, (1,len(y))) if len(y.shape) == 1 else y # single-channel check
    return (f,y)


class AudioFetcher():
    '''
    Description: audio fetcher class, grabs chunks of audio based on parameters
    '''
    def __init__(self, interval, wav_dir='/data/kraken/teams/acoustic_data/ais_data_labeling/wav/harp/', wav_fmt='harp', sample_rate=4000, segment_length_seconds=30):
        '''
        Description: audio fetcher constructor

        :interval: tuple in nanoseconds (ns, ns)
        :wav_dir: directory of wav files
        :wav_fmt: mars or harp
        :sample_rate: sample rate of audio
        :segment_length_seconds: length of segments to generate in seconds
        '''
        self.wav_dir = wav_dir
        self.wav_fmt = wav_fmt
        self.sample_rate = sample_rate
        self.segment_length_seconds = segment_length_seconds  
        self.segment_length_samples = self.sample_rate*self.segment_length_seconds
        self.mono = wav_fmt == 'harp'

        try:
            assert interval[0] < interval[1]
            self.interval = interval
        except:
            raise Exception("Not a valid interval")

        self.target_wavs = self._generate_target_wavs()

        self.target_wavs_filenames = [wav_pair[0] for wav_pair in self.target_wavs]
        self.wav_segments = [] 
    
    def generate_wav_segments(self):
        '''
        This function works assuming that the file_paths being passed in are a result of 
        target_wavs() from the audio fetcher for the passed in interval
        :interval: [start, end]
        :file_paths: a list of paths to wav files
        '''
        audio_start_nanos = self.interval[0]
        start = self.interval[0] / (1e9) # start from nanoseconds to seconds
        end = self.interval[1] / (1e9) # end from nanoseconds to seconds
        
        first_file_sec = wav_path_to_nanos(self.wav_fmt, self.target_wavs_filenames[0]) / 1e9
        last_file_sec = wav_path_to_nanos(self.wav_fmt, self.target_wavs_filenames[-1]) / 1e9

        start_bin = int((start - first_file_sec) // 30)
        last_bin = int((end - last_file_sec) // 30)
        print(f'start bin: {start_bin} last bin: {last_bin}')
        segment_length_nanos = self.segment_length_seconds * 1e9

        # split all the files
        for index, file in enumerate(self.target_wavs_filenames):
            print(file)
            # load the file
            try:
                file, wave = load_wav(file, self.sample_rate, self.mono)
            except:
                print("Error loading the file")
                continue
            

            # split the file into 30 second chunks and save
            num_sections = int(np.ceil(wave.shape[1] / self.segment_length_samples))
            print(num_sections)

            # create a check to see if the last bin and start bin are in the same file
            if len(self.target_wavs) == 1:
                for i in range(start_bin, last_bin):
                    t = self._create_segment_wav(wave, i * self.segment_length_samples, (i + 1) * self.segment_length_samples)
                    print(t.shape)
                    self.wav_segments.append([audio_start_nanos, t])
                    audio_start_nanos += segment_length_nanos

            elif index == 0:
                for i in range(start_bin, num_sections):
                    t = self._create_segment_wav(wave, i * self.segment_length_samples, (i + 1) * self.segment_length_samples)
                    print(t.shape)
                    self.wav_segments.append([audio_start_nanos, t])
                    audio_start_nanos += segment_length_nanos

            elif index == len(self.target_wavs) - 1:
                for i in range(last_bin):
                    t = self._create_segment_wav(wave, i * self.segment_length_samples, (i + 1) * self.segment_length_samples)
                    print(t.shape)
                    self.wav_segments.append([audio_start_nanos, t])
                    audio_start_nanos += segment_length_nanos
            else:
                for i in range(num_sections):
                    t = self._create_segment_wav(wave, i * self.segment_length_samples, (i + 1) * self.segment_length_samples)
                    print(t.shape)
                    self.wav_segments.append([audio_start_nanos, t])
                    audio_start_nanos += segment_length_nanos




    def _generate_target_wavs(self):
        '''
        Description: generates target wav files based on interval supplied to audio fetcher
        '''
        wav_paths = glob.glob(os.path.join(self.wav_dir, '*.wav'))
        df = pd.DataFrame(wav_paths, columns=['path'])
        df['wav_start_nanos'] = df['path'].apply(lambda x: wav_path_to_nanos(self.wav_fmt, x))

        istrt_nanos = self.interval[0]
        istop_nanos = self.interval[1]
        print(f'istart_nanos {istrt_nanos}')
        print(f'istop_nanos {istop_nanos}')

        df = df.sort_values('wav_start_nanos', ignore_index=True) # ascending
        row_start = np.argmax(istrt_nanos <= df['wav_start_nanos'].values) 
        row_end   = np.argmax(istop_nanos <= df['wav_start_nanos'].values)

        if istrt_nanos < df['wav_start_nanos'][row_start]:
            row_start -= 1
            
        if row_end - row_start >= 0:
            row_end += 1
        # else:
        #     row_end -= 1
        print(f'this is the row_start and end {row_start} {row_end}')
        paths = df['path'           ][row_start:row_end-1].values
        strts = df['wav_start_nanos'][row_start:row_end-1].values
        interval_wavs = sorted([(p,s) for p, s in zip(paths, strts)], key=lambda x: x[1])
        return interval_wavs

    def _create_segment_wav(self, wave, start, end):
        '''
        Description: creates wav segment based on parameters

        :wave: audio in numpy format
        :start: start index of segment
        :end: end index of segment
        '''
        channel_segs = []
        for channel in wave:
            channel_segs.append(channel[start:end])
        t = np.vstack(channel_segs) 
        return t
       