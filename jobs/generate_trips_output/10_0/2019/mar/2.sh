#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/10_0/2019/mar/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 10 \
--buffer 0 \
--start "20190310 000000" \
--end "20190320 000000" \
--year 2019 \
--month mar \
--portion 2
