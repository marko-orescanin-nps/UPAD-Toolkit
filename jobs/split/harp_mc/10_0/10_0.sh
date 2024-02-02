#!/bin/bash
#SBATCH --output=outputs/split_10_0_mc.out
#SBATCH --time=10:00:00
#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34

python -m split.split --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/10_0/' \
                      --tfrecords_pkl 'query/harp_intervals/10_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D10_B0_mc/'