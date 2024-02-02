#!/bin/bash 
#SBATCH --output=outputs/create_records_pickle_harp_7.5_0_mc.out \
#SBATCH --time=24:00:00 \
#SBATCH --nodes=1 \
#SBATCH --partition=kraken \
#SBATCH --nodelist=compute-9-34 \
#SBATCH --cpus-per-task=128 \
#SBATCH --mem=990G


python3 -m tools.create_records_pickle --record_dir "/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/7.5_0" \
                                       --output_pickle "/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/7.5_0/lut.pickle"