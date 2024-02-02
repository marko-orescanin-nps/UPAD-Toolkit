#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/15_0/2019/jan/3.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 15 \
--buffer 0 \
--start "20190120 000000" \
--end "20190201 000000" \
--year 2019 \
--month jan \
--portion 3
