#!/bin/bash
#SBATCH --output=outputs/label_counts_5_0_test_6_month.out
#SBATCH --time=1000:00:00
#SBATCH --partition=kraken
#SBATCH --nodelist=compute-9-34

python -m tools.label_counts --record_dir '/data/kraken/teams/acoustic_data/ais_data_labeling/splits/harp/0.1.1/D5_B0_2018_2021/test_6_month/'