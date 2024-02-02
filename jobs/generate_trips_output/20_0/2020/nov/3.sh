#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/20_0/2020/nov/3.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 20 \
--buffer 0 \
--start "20201120 000000" \
--end "20201201 000000" \
--year 2020 \
--month nov \
--portion 3
