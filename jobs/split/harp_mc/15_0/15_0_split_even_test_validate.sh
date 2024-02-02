#!/bin/bash
#SBATCH --output=outputs/split_15_0_mc_even_test_validate.out

#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34


python -m split.split_even_test_validate --records_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/15_0/' \
                      --tfrecords_pkl 'query/harp_intervals/15_0.pickle' \
                      --output_path '/thumper/users/kraken/ais_data_labeling/splits/D15_B0_mc/'