#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/5_0/2019/sept/3.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 5 \
--buffer 0 \
--start "20190920 000000" \
--end "20191001 000000" \
--year 2019 \
--month sept \
--portion 3
