#!/bin/bash
#SBATCH --output=outputs/generate_trips_output/5_0/2020/dec/2.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \


python3 -m tools.generate_trips_output \
--detect 5 \
--buffer 0 \
--start "20201210 000000" \
--end "20201220 000000" \
--year 2020 \
--month dec \
--portion 2
