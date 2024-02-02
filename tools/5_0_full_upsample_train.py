from utils.split_utils import upsample

split_filename = "/thumper/users/kraken/ais_data_labeling/splits/D5_B0_mc/train.txt"
output_filename = "/thumper/users/kraken/ais_data_labeling/splits/D5_B0_mc/full_upsample_train.txt"
rate = 27

upsample(split_filename, output_filename, rate)