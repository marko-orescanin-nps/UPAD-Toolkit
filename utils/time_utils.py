from pytz import timezone, utc
import datetime

def greg_to_nanos(time):
    '''Convert .mat file `datenumber` field, which is in proleptic Gregorian 
    ordinal format in UTC timezone, to nanoseconds since the epoch.'''

    whole_days = datetime.datetime.fromordinal(int(time))
    frac_days = datetime.timedelta(days=time%1)
    #  http://sociograph.blogspot.com/2011/04/how-to-avoid-gotcha-when-converting.html
    matlab_to_python_correction = datetime.timedelta(days=366)
    nanos = (whole_days + frac_days - matlab_to_python_correction).timestamp()*10**9
    return nanos

def user_date_to_nanos(date_str):
    '''Convert user-supplied `date_str` to nanoseconds since the epoch. 
    `user_str` has format "YYYYMMDD HHMMSS". User-supplied date strings are
    assumed to be in UTC timezone.
    '''
    year  = int(date_str[0 :4 ])
    month = int(date_str[4 :6 ])
    day   = int(date_str[6 :8 ])
    hour  = int(date_str[9 :11])
    min   = int(date_str[11:13])
    sec   = int(date_str[13:15])

    return int(datetime.datetime(year, month, day, hour, min, sec, tzinfo=timezone('UTC')).timestamp()*10**9)

def uscg_date_to_nanos(date_str):
    '''
    Convert date strings in uscg AIS csv data to nanoseconds
    Format: 2018-11-01T00:00:02
    '''
    year = int(date_str[0:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    hour = int(date_str[11:13])
    min = int(date_str[14:16])
    sec = int(date_str[17:19])

    return int(datetime.datetime(year, month, day, hour, min, sec, tzinfo=timezone('UTC')).timestamp()*10**9)

def mat_filename_to_nanos(mat_filename):
    '''Convert .mat filename `mat_filename` to nanoseconds since the epoch. 
    `mat_filename` has format "YYMMDD.mat" and is assumed to be in UTC timezone.
    '''
    year  = 2000 + int(mat_filename[0:2])
    month = int(mat_filename[2:4])
    day   = int(mat_filename[4:6])
    
    return int(datetime.datetime(year, month, day, tzinfo=timezone('UTC')).timestamp()*10**9)


def uscg_ais_to_nanos(ais_filename: str):
    '''
    Format: USCG_AIS_5min_MB_2021-01.csv
    '''
    date = ais_filename.split('.')[0].split('_')[-1]
    year, month = date.split('-')
    return int(datetime.datetime(int(year), int(month), 1, tzinfo=timezone('UTC')).timestamp()*10**9)

def marine_cadastre_to_nanos(ais_filename: str):
    '''
    Format: 2019-01.csv
    '''
    year, month = ais_filename.split('.')[0].split('-')[:2]
    return int(datetime.datetime(int(year), int(month), 1, tzinfo=timezone('UTC')).timestamp()*10**9)

def surridge_to_harp_audio(filename: str):
    # SurRidge_PS18_220124_012115.x.wav example string
    ymd, hms = filename.split('.x.wav')[0].split('_')[2:]
    ymd = '20' + ymd
    return f"harp_{ymd}{hms}.x.wav"

def wav_str_to_nanos(wav_str):
    '''Convert .wav date string `wav_str` to nanoseconds since the epoch. 
    `wav_str` has format "YYYYMMDDHHMMSS" and is assumed to 
    be in UTC timezone.
    '''
    year  = int(wav_str[0 :4 ])
    month = int(wav_str[4 :6 ])
    day   = int(wav_str[6 :8 ])
    hour  = int(wav_str[8 :10])
    min   = int(wav_str[10:12])
    sec   = int(wav_str[12:14])
    
    return int(datetime.datetime(year, month, day, hour, min, sec, tzinfo=timezone('UTC')).timestamp()*10**9)

def wav_path_to_nanos(wav_fmt, filename):
    if wav_fmt == 'mars':
        # .wav filename schema: m209_oxyz_20211203152515.wav
        date_str = filename[-18:-4]
        nanos = wav_str_to_nanos(date_str)
    elif wav_fmt == 'harp':
        # .wav filename schema: harp_20181114000000.x.wav
        date_str = filename[-20:-6]
        nanos = wav_str_to_nanos(date_str)
    else:    
        raise Exception('Unknown .wav format {}'.format(wav_fmt))
    return nanos
       

def utc_to_nanos(timestamp: str, start=False, end=False):
    # 2018-11-14T03:46:50.000Z
    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hour = int(timestamp[11:13])
    minute = int(timestamp[14:16])
    second = int(timestamp[17:19])
    if start:
        hour = minute = second = 0
    if end:
        hour = 23
        minute = 59
        second = 59
    return int(datetime.datetime(year, month, day, hour, minute, second, tzinfo=timezone('UTC')).timestamp()*10**9)

def nanos_to_day(nanos):
    day = datetime.datetime.fromtimestamp(nanos/10**9, tz=utc).day
    return day

def nanos_to_week(nanos):
    week = datetime.datetime.fromtimestamp(nanos/10**9, tz=utc).isocalendar()[1]
    return week

def nanos_to_month(nanos):
    month = datetime.datetime.fromtimestamp(nanos/10**9, tz=utc).month
    return month

def nanos_to_year(nanos):
    year = datetime.datetime.fromtimestamp(nanos/10**9, tz=utc).year
    return year

def nanos_to_ymd_str(nanos):
    dt = datetime.datetime.fromtimestamp(nanos/10**9,tz=utc)
    year_str = convert_single_digit(dt.year)
    month_str = convert_single_digit(dt.month)
    day_str = convert_single_digit(dt.day)
    hour_str = convert_single_digit(dt.hour)
    min_str = convert_single_digit(dt.minute)
    sec_str = convert_single_digit(dt.second)
    dt_str = f'{year_str}{month_str}{day_str} {hour_str}{min_str}{sec_str}'
    return dt_str

def convert_single_digit(date_val: int) -> str:
    if date_val % 10 == date_val:
        return '0' + str(date_val)
    else:
        return str(date_val)
