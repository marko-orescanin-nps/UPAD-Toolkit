from utils.split_utils import upsample

split_filename = "/thumper/users/kraken/ais_data_labeling/splits/D7.5_B0_mc/train.txt"
output_filename = "/thumper/users/kraken/ais_data_labeling/splits/D7.5_B0_mc/full_upsample_train.txt"
rate = 11

upsample(split_filename, output_filename, rate)