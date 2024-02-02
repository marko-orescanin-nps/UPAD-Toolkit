import os

month_to_num = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "aug": "08",
    "sept": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12"
}

def generate_script(month, section, year, detect, buffer, start_end_days):
    if section == 3:
        if month == "dec":
            new_month = "01"
            end_string = f"{year + 1}{new_month}{start_end_days[1]}"
        else:
            new_month = (int(month_to_num[month]) + 1)
            if new_month < 10:
                new_month = '0' + str(new_month)

            end_string = f"{year}{new_month}{start_end_days[1]}"
    else:
        end_string = f"{year}{month_to_num[month]}{start_end_days[1]}"
    script = f'''#!/bin/bash\

#SBATCH --output=outputs/generate_trips_output/{detect}_{buffer}/{year}/{month}/{section}.out \\
#SBATCH --time=48:00:00 \\
#SBATCH --nodes=1 \\
#SBATCH --mem=128G \\
#SBATCH --ntasks=1 \\


python3 -m tools.generate_trips_output \\
--detect {detect} \\
--buffer {buffer} \\
--start "{year}{month_to_num[month]}{start_end_days[0]} 000000" \\
--end "{end_string} 000000" \\
--year {year} \\
--month {month} \\
--portion {section}
'''
    return script

if __name__ == '__main__':
    start_end_days = [["01", "10"], ["10", "20"], ["20", "01"]]
    detect_ranges = [2.5, 5, 7.5, 10, 15, 20, 30]
    buffer_ranges = [0]

    years = [2018, 2019, 2020, 2021]
    years_map = {
        2018: ["dec", "nov"],
        2019: ["april", "aug", "dec", "feb", "jan", "july", "june", "mar", "may", "nov", "oct", "sept"],
        2020: ["april", "aug", "dec", "feb", "jan", "july", "june", "mar", "may", "nov", "oct", "sept"],
        2021: ["april", "aug", "dec", "feb", "jan", "july", "june", "mar", "may", "nov", "oct", "sept"]
    }
    for detect in detect_ranges:
        for buffer in buffer_ranges:
            for year in years:
                for month in years_map[year]:
                    for section in range(1, 4):
                        script = generate_script(month, section, year, detect, buffer, start_end_days[section-1])
                        if not os.path.exists(f"jobs/generate_trips_output/{detect}_{buffer}/{year}/{month}"):
                            os.makedirs(f"jobs/generate_trips_output/{detect}_{buffer}/{year}/{month}")
                        output_path = f"jobs/generate_trips_output/{detect}_{buffer}/{year}/{month}/{section}.sh"
                        with open(output_path, "w+") as f:
                            f.write(script)
                    
