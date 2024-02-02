#!/bin/bash 
#SBATCH --output=outputs/ground_truth/july_2019_3_5_0.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

python3 -m ground_truth --start "20190720 000000" \
                        --end "20190801 000000" \
                        --ais_data "samples/5_0/july_2019_3_5_0.csv" \
                        --output "ground_truth_matrix/5_0/july_2019_3_5_0.pickle" \
