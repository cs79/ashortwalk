# imports
import pandas as pd
import os, gpxpy
import matplotlib.pyplot as plt

# working directory metadata
gpx_dir_path = 'C:/users/cloud/Dropbox/Projects/ashortwalk/gpxdata'
os.chdir(gpx_dir_path)

# GPX parsing functions
parse_gpx = lambda x: gpxpy.parse(open(x, 'r'))

def summarize_points(track):
    '''
    Given a track, pull out GPXTrackPoints as a pandas dataframe.
    '''
    df = pd.DataFrame()
    pts = track.get_points_data()
    for i in range(len(pts)):
        pt = pts[i][0]
        dist = pts[i][1]
        # ti = pt.time.isoformat()
        df.loc[i, 'datetime'] = pd.Timestamp(pt.time.isoformat())
        df.loc[i, 'lat'] = pt.latitude
        df.loc[i, 'long'] = pt.longitude
        df.loc[i, 'elevation'] = pt.elevation
        df.loc[i, 'dist_from_start'] = dist
    # df.index = pd.DatetimeIndex(df.index)
    return(df)

def find_eod_index(df):
    '''
    Helper function to find index of end of day for paused data.
    '''
    eods = []
    for i in range(1, len(df)):
        time_diff = df.loc[i, 'datetime'] - df.loc[(i-1), 'datetime']
        if time_diff.seconds > (60**2 * 8):
            eods.append(df.index[i-1])
            print('Found likely EOD candidate: {}'.format(df.loc[(i-1), 'datetime']))
    return(eods)


# figure out what all is in these things:
day1track = parse_gpx('GAIA_Dushanbe_to_Khorog_8_4_19_5_21_57_AM.gpx')
first5 = parse_gpx('GAIA_First_five_days_of_trek_8_8_19_8_53_03_AM.gpx')
# no day 6; stuck at Kyrgyz settlement
day7 = parse_gpx('GAIA__Trek_Day_7_8_14_19_8_13_29_AM.gpx')
day8 = parse_gpx('GAIA_Trek_Day_8_8_15_19_8_37_01_AM.gpx')
day9 = parse_gpx('GAIA_Trek_Day_9_8_16_19_4_22_53_AM.gpx')
day10 = parse_gpx('GAIA_Trek_Day_10_8_17_19_10_48_05_AM.gpx')
day11_partial = parse_gpx('GAIA_Trek_Day_11_(partial)_8_18_19_8_20_13_AM.gpx')

# "day1" track needs to be split properly into the 5 days
f5df = summarize_points(first5)
candidate_eods = find_eod_index(f5df)
# this looks weird somehow - look into this further
# maybe use an integer index and then a time column for df format
# when wanting to plot elevation charts, can switch to a datetime index
td1 = f5df.loc[0:candidate_eods[1],:]
td2 = f5df.loc[candidate_eods[1]+1:candidate_eods[3],:]
td3 = f5df.loc[candidate_eods[3]+1:candidate_eods[5],:]
td4 = f5df.loc[candidate_eods[5]+1:candidate_eods[7],:]
td5 = f5df.loc[candidate_eods[7]+1:f5df.index[-1],:]
# no td6 - stuck at Kyrgyz settlement
td7 = summarize_points(day7)
td8 = summarize_points(day8)
td9 = summarize_points(day9)
td10 = summarize_points(day10)
td11_partial = summarize_points(day11_partial)

# summarize each day (distance, elevation +/-/net, elapsed time)

# also get a "full trek" altitude profile; i guess assume even spacing of pts?
