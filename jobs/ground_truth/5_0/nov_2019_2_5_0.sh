#!/bin/bash 
#SBATCH --output=outputs/ground_truth/nov_2019_2_5_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20191110 000000" \
                        --end "20191120 000000" \
                        --ais_data "samples/5_0/nov_2019_2_5_0.csv" \
                        --output "ground_truth_matrix/5_0/nov_2019_2_5_0.pickle" \
