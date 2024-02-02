import os
import numpy as np
import tensorflow as tf
from math import ceil
import matplotlib.pyplot as plt
import librosa

'''
    Author:  Major John Fischer
    Project:  Passive Sonar Classifier

    Module Description:  Module contains functions used to plot audio samples in the form of spectrograms for visualization.   

'''

'''
    Helper function to retrieve bin index of a specific frequency.  
    
    Args:
        frequency - target frequency
        sample_points - fft_length in samples
        sample_rate - sample rate of audio
    
    Returns:
        bin - frequency bin of the target frequency
'''
def get_bin_index(frequency, sample_points, sample_rate):
    bin = ceil((frequency*sample_points) / sample_rate)
    return bin

'''
    Helper function to retrieve pressure_channel of audio for plotting

    Args:
        filepath - absolute path to audio sample
        is_multi_channel - boolean.  True if audio sample is a multi_channel sample
    
    Returns:
        audio - decoded audio sample
'''
def get_audio(filepath, is_multi_channel):
    if is_multi_channel:
        audio, _ = librosa.load(filepath, sr = 4000, mono=False)
        audio = audio[0]
    else:
        audio, _ = librosa.load(filepath, sr = 4000, mono=True)
    
    return audio


'''
    Function to plot STFT Spectrogram and Mel Spectrogram of a single channel audio sample.  Default parameters are based on 
    hyperparameter settings from Vector Sensor Paper (IEEE JoE).

    Args:
        audio - single channel audio sample
        win_size - size of STFT window in ms
        overlap - overlap percentage (0-100)
        sample_points - fft_length in samples
        sample_rate - sample rate of audio
        duration - length of sample in seconds
        min_freq - minimum desired frequency 
        max_freq - maximum desired frequency -- should not be any greater than sample_rate / 2 (Nyquist Freq)
        filterDC - boolean.  If True, 500Hz distortion will be filtered out (430-570Hz)
        mel_bins - number of Mel Bins to output
    
    Returns:
        N/A
'''
def plot_spectrogram(audio, win_size=256, overlap=50, sample_points=1024, sample_rate=4000, duration=30, min_freq=0, max_freq=2000,
                                filterDC=False, mel_bins=128):
    
    #Convert from time (ms) to samples
    WIN_SIZE = (int)((win_size * .001) * sample_rate)

    #Compute step length in samples
    STEP = (int)(WIN_SIZE-((overlap / 100) * WIN_SIZE))

    #Number of MEL Freq Bins
    MEL_BINS = mel_bins

    #Number of STFT Freq Bins -- sample_points is FFT_Length in samples
    STFT_BINS = (sample_points // 2) + 1

    if min_freq == 0:
        LOWER_BOUND = 0
        BIN_LOW = 0
    else:
        BIN_LOW = get_bin_index(min_freq)
        LOWER_BOUND = (BIN_LOW * sample_rate) // sample_points
    if max_freq == 2000:
        UPPER_BOUND = sample_rate / 2
        BIN_HIGH = STFT_BINS-1
    else:
        BIN_HIGH = get_bin_index(max_freq)
        UPPER_BOUND = ceil((BIN_HIGH * sample_rate) / sample_points)

    TIME_SPACE = ceil((duration * sample_rate) / STEP)

    if filterDC:
        NUM_SPEC_BINS = BIN_HIGH - BIN_LOW - 36
    else:
        NUM_SPEC_BINS = BIN_HIGH - BIN_LOW + 1
    
    #Remove extra dimension (120000,1) to (120000,)
    audio_squeeze = tf.reshape(tf.squeeze(audio), [1,-1])

    stfts = tf.signal.stft(audio_squeeze, frame_length=WIN_SIZE, frame_step=STEP,
                            fft_length=sample_points, window_fn=tf.signal.hann_window, pad_end=True)
    
    mag_spec_base = tf.abs(stfts)

    if filterDC:
        mag_spec_base = tf.concat([mag_spec_base[:, :, BIN_LOW:110], mag_spec_base[:, :, 147:]], 2)
    else:
        #Filter out unwanted frequencies
        mag_spec_base = mag_spec_base[:,:,BIN_LOW:BIN_HIGH + 1]
        
    #Compute linear to mel weight matrix
    linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(MEL_BINS, NUM_SPEC_BINS, sample_rate, LOWER_BOUND, UPPER_BOUND)

    #Mel Spectrogram is in [channels, freq, time] format
    mel_spectrograms = tf.tensordot(mag_spec_base, linear_to_mel_weight_matrix, 1)

    # Compute a stabilized log to get log-magnitude mel-scale spectrograms.
    log_mel_spectrograms = 20 * tf.math.log(mel_spectrograms/tf.math.reduce_max(mel_spectrograms) + 1e-6)/2.303
    
    #Convert Spectrograms to db scale
    # Spectrogram is in [channels, freq, time] format
    log_spectrograms = 20 * tf.math.log(mag_spec_base/tf.math.reduce_max(mag_spec_base) + 1e-6)/2.303

    #Create scales for spectrogram plot x,y axis
    mel_vector = np.linspace(min_freq, 2595*(np.log10(1+(max_freq/700))), num=MEL_BINS)
    freq_vector = np.linspace(min_freq, max_freq, num=NUM_SPEC_BINS)
    frame_vector_time = np.linspace(0, duration, num=TIME_SPACE)

    cmap = plt.cm.get_cmap("jet")
    
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.linewidth'] = 1

    fig, axs = plt.subplots(nrows=1,ncols=2, sharex=True, figsize=(20,4), constrained_layout=True)

    pcm = axs[0].pcolormesh(frame_vector_time, freq_vector, np.transpose(np.squeeze(log_spectrograms.numpy(), 0)),cmap=cmap)
    axs[0].set_title('STFT Spectrogram')
    axs[0].set(xlabel='Time [sec]')
    axs[0].set(ylabel='Frequency [Hz]')

    pcm = axs[1].pcolormesh(frame_vector_time, mel_vector, np.transpose(np.squeeze(log_mel_spectrograms.numpy(), 0)),cmap=cmap)
    axs[1].set_title('Mel Spectrogram')
    axs[1].set(xlabel='Time [sec]')
    axs[1].set(ylabel='Frequency [Mel]')
     
    fig.colorbar(pcm,ax=axs[1], shrink=0.6)
    
    plt.show()
    plt.close('all')
