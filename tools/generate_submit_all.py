import os

if __name__ == '__main__':
    detect_ranges = [5, 10, 15, 20, 30]
    buffer_ranges = [0]
    scripts_dir = 'jobs/generate_trips_output'

    result = []
    for detect in detect_ranges:
        for buffer in buffer_ranges:
            print(detect, buffer)
            for year in sorted(os.listdir(scripts_dir + f"/{detect}_{buffer}")):
                if '.sh' not in year:
                    for month in os.listdir(f'{scripts_dir}/{detect}_{buffer}/{year}'):
                        result.append(f"sbatch {scripts_dir}/{detect}_{buffer}/{year}/{month}/1.sh\n")
                        result.append(f"sbatch {scripts_dir}/{detect}_{buffer}/{year}/{month}/2.sh\n")
                        result.append(f"sbatch {scripts_dir}/{detect}_{buffer}/{year}/{month}/3.sh\n")
            with open(f'{scripts_dir}/submit_D{detect}_B{buffer}.sh', 'w+') as f:
                f.write("#!/bin/bash\n")
                f.writelines(result)
                result = []
            
