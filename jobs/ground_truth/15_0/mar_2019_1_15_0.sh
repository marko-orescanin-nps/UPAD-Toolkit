#!/bin/bash 
#SBATCH --output=outputs/ground_truth/mar_2019_1_15_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20190301 000000" \
                        --end "20190310 000000" \
                        --ais_data "samples/15_0/mar_2019_1_15_0.csv" \
                        --output "ground_truth_matrix/15_0/mar_2019_1_15_0.pickle" \
