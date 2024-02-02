#!/bin/bash 
#SBATCH --output=outputs/ground_truth/june_2020_1_15_0.0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m tools.ground_truth --start "20200601 000000" \
                        --end "20200610 000000" \
                        --ais_data "samples/15_0.0/june_2020_1_15_0.0.csv" \
                        --output "ground_truth_matrix/15_0.0/june_2020_1_15_0.0.pickle" \
