#!/bin/bash 
#SBATCH --output=outputs/ground_truth/dec_2019_2_10_0.0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m tools.ground_truth --start "20191210 000000" \
                        --end "20191220 000000" \
                        --ais_data "samples/10_0.0/dec_2019_2_10_0.0.csv" \
                        --output "ground_truth_matrix/10_0.0/dec_2019_2_10_0.0.pickle" \
