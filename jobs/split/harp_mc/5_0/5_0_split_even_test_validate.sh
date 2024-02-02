#!/bin/bash
#SBATCH --output=outputs/split_5_0_mc_even_test_validate.out
#SBATCH --time=1000:00:00
#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34

python -m split.split_even_test_validate --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/5_0/' \
                      --tfrecords_pkl 'query/harp_intervals/5_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D5_B0_mc/'