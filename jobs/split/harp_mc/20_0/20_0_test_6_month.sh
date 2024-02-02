#!/bin/bash
#SBATCH --output=outputs/split_20_0_test_6_month.out

#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34



python -m split.split_test_6month --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/20_0/' \
                      --tfrecords_pkl 'query/harp_intervals/20_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D20_B0_mc/test_6_month/'