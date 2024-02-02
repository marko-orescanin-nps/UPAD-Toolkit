#!/bin/bash 
#SBATCH --output=outputs/ground_truth/nov_2020_1_15_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20201101 000000" \
                        --end "20201110 000000" \
                        --ais_data "samples/15_0/nov_2020_1_15_0.csv" \
                        --output "ground_truth_matrix/15_0/nov_2020_1_15_0.pickle" \
