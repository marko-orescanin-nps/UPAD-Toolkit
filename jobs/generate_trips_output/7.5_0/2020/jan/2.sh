#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/7.5_0/2020/jan/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 7.5 \
--buffer 0 \
--start "20200110 000000" \
--end "20200120 000000" \
--year 2020 \
--month jan \
--portion 2
