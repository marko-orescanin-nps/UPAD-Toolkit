import os


def generate_script(section, detect, buffer):
    
    script = f'''#!/bin/bash\

#SBATCH --output=outputs/split_modifier_{detect}_{buffer}_{section}.out
#SBATCH --time=96:00:00
python -m split.split_modifier --records_dir '/data/kraken/teams/acoustic_data/ais_data_labeling/multilabel_tfrecords/harp/0.1.1/{detect}_{buffer}/' \\
                         --split_dir '/thumper/users/kraken/ais_data_labeling/splits/D{detect}_B{buffer}/' \\
                         --output_dir '/thumper/users/kraken/ais_data_labeling/splits/D{detect}_B{buffer}/{section}/' \\
                         --section '{section}' \\
                         --downsample 0 \\
                         --upsample 0 \\
                         --num_channels 1 \\
                         --audio_preprocess true
'''
    return script

if __name__ == '__main__':
    for section in ['full_even_test', 'full_even_validate', 'full_train', 'full_upsample_train', 'test_6_month']:
        for detect in [10, 15]:
            for buffer in [0, 5, 10]:
                script = generate_script(section, detect, buffer)
                if not os.path.exists(f"jobs/split_modifier/harp/{detect}_{buffer}"):
                    os.makedirs(f"jobs/split_modifier/harp/{detect}_{buffer}")
                output_path = f"jobs/split_modifier/harp/{detect}_{buffer}/{section}.sh"
                with open(output_path, "w+") as f:
                    f.write(script)

