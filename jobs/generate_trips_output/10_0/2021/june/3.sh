#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/10_0/2021/june/3.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 10 \
--buffer 0 \
--start "20210620 000000" \
--end "20210701 000000" \
--year 2021 \
--month june \
--portion 3
