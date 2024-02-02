#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/30_0/2020/april/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 30 \
--buffer 0 \
--start "20200410 000000" \
--end "20200420 000000" \
--year 2020 \
--month april \
--portion 2
