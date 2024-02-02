#!/bin/bash
#SBATCH --output=outputs/harp_marine/tfrecord_gen_dec_3_5_10_2020.out \
#SBATCH --time=48:00:00 \
#SBATCH --nodes=1 \
#SBATCH --mem=128G \
#SBATCH --ntasks=1 \
#SBATCH --cpus-per-task=11 \

source activate mbayarr
python -O -W ignore -m src.main \
--tfrecord_audio 'raw' \
--ais_data '/data/kraken/teams/acoustic_data/ais_data_labeling/ais_data/MarineCadastre_0/' \
--wav_dir '/data/kraken/teams/acoustic_data/ais_data_labeling/wav/harp/' \
--wav_fmt 'harp' \
--tfrecord_dir '/thumper/users/kraken/ais_data_labeling/multilabel_tfrecords/MarineCadastre/5_10/' \
--detect_range 5 \
--buffer_range 10 \
--start "20201220 000000" \
--end "20210101 000000" \
--mmsi_meta_cache '/data/kraken/teams/acoustic_data/ais_data_labeling/mmsi_meta_cache/MarineCadastre/cache.csv' \
--sample_rate 4000 \
--segment_length_seconds 30 \
--uscg_or_marine 'marine'
