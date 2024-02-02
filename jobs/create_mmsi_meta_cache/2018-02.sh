#!/bin/bash

#SBATCH --output=outputs/2018-02.out
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --mem=128G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=11

source activate mbayarr
python -m create_mmsi_meta_cache --uscg_dir '/work_new/kraken/AIS/USCG/' \
                                 --csv_file 'USCG_AIS_5min_MB_2018-02.csv' \
                                 --base_meta_cache '/data/kraken/MBAY_AIS_AUDIO/uscg_mmsi_meta_2018-02.csv' \
                                 --output_file '/data/kraken/MBAY_AIS_AUDIO/uscg_mmsi_meta_2018-02.csv'