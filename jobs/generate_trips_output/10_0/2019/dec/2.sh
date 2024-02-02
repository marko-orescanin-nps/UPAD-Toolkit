#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/10_0/2019/dec/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 10 \
--buffer 0 \
--start "20191210 000000" \
--end "20191220 000000" \
--year 2019 \
--month dec \
--portion 2
