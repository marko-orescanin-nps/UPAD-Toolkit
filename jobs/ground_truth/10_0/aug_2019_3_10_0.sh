#!/bin/bash 
#SBATCH --output=outputs/ground_truth/aug_2019_3_10_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20190820 000000" \
                        --end "20190901 000000" \
                        --ais_data "samples/10_0/aug_2019_3_10_0.csv" \
                        --output "ground_truth_matrix/10_0/aug_2019_3_10_0.pickle" \
