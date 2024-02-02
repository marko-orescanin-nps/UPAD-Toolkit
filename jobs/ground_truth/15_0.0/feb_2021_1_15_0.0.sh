#!/bin/bash 
#SBATCH --output=outputs/ground_truth/feb_2021_1_15_0.0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m tools.ground_truth --start "20210201 000000" \
                        --end "20210210 000000" \
                        --ais_data "samples/15_0.0/feb_2021_1_15_0.0.csv" \
                        --output "ground_truth_matrix/15_0.0/feb_2021_1_15_0.0.pickle" \
