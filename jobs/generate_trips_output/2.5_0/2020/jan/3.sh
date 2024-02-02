#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/2.5_0/2020/jan/3.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 2.5 \
--buffer 0 \
--start "20200120 000000" \
--end "20200201 000000" \
--year 2020 \
--month jan \
--portion 3
