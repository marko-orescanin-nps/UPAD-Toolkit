#!/bin/bash 
#SBATCH --output=outputs/ground_truth/nov_2018_1_20_0.0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m tools.ground_truth --start "20181101 000000" \
                        --end "20181110 000000" \
                        --ais_data "samples/20_0.0/nov_2018_1_20_0.0.csv" \
                        --output "ground_truth_matrix/20_0.0/nov_2018_1_20_0.0.pickle" \
