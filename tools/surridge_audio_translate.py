from utils.time_utils import surridge_to_harp_audio

import shutil
import os

if __name__ == '__main__':
    input_dir = '/data/kraken/teams/acoustic_data/MBAY_SANCT_SOUND/MB03_05/Disk05/XWAV/'
    output_dir = '/data/kraken/teams/acoustic_data/ais_data_labeling/wav/harp/'

    existing_files = set(os.listdir(output_dir))
    print("created set")

    for file in os.listdir(input_dir):
        print(file)
        if '.x.wav' in file:
            harp_file = surridge_to_harp_audio(file)
            if harp_file not in existing_files:
                print('copying:', harp_file)
                shutil.copy(input_dir + file, output_dir + harp_file)