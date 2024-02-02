#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/30_0/2019/may/1.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 30 \
--buffer 0 \
--start "20190501 000000" \
--end "20190510 000000" \
--year 2019 \
--month may \
--portion 1
