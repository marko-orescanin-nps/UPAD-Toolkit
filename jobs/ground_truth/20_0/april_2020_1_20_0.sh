#!/bin/bash 
#SBATCH --output=outputs/ground_truth/april_2020_1_20_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20200401 000000" \
                        --end "20200410 000000" \
                        --ais_data "samples/20_0/april_2020_1_20_0.csv" \
                        --output "ground_truth_matrix/20_0/april_2020_1_20_0.pickle" \
