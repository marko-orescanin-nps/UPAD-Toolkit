#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/30_0/2021/feb/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 30 \
--buffer 0 \
--start "20210210 000000" \
--end "20210220 000000" \
--year 2021 \
--month feb \
--portion 2
