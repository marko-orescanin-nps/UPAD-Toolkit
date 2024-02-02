#!/bin/bash
#SBATCH --output=outputs/split_7.5_0_test_6_month.out

python -m split.split_test_6month --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/7.5_0/' \
                      --tfrecords_pkl 'query/harp_intervals/7.5_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D7.5_B0_mc/test_6_month/'