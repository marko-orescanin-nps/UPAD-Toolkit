#!/bin/bash
#SBATCH --output=outputs/split_7.5_0_mc_even_test_validate.out
#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34

python -m split.split_even_test_validate --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/7.5_0/' \
                      --tfrecords_pkl 'query/harp_intervals/7.5_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D7.5_B0_mc/'