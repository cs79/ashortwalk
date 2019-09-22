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
        ti = pt.time.isoformat()
        df.loc[ti, 'lat'] = pt.latitude
        df.loc[ti, 'long'] = pt.longitude
        df.loc[ti, 'elevation'] = pt.elevation
        df.loc[ti, 'dist_from_start'] = dist
    df.index = pd.DatetimeIndex(df.index)
    return(df)

def find_eod_index(df):
    '''
    Helper function to find index of end of day for paused data.
    '''
    eods = []
    for i in range(1, len(df)):
        time_diff = df.index[i] - df.index[i-1]
        if time_diff.seconds > (60**2 * 8):
            eods.append(df.index[i-1])
            print('Found likely EOD candidate: {}'.format(df.index[i-1]))
    return(eods)


# figure out what all is in these things:
day1track = parse_gpx('GAIA_Dushanbe_to_Khorog_8_4_19_5_21_57_AM.gpx')
first5 = parse_gpx('GAIA_First_five_days_of_trek_8_8_19_8_53_03_AM.gpx')

# "day1" track needs to be split properly into the 5 days
first5df = summarize_points(first5)
candidate_eods = find_eod_index(first5df)
# this looks weird somehow - look into this further
# maybe use an integer index and then a time column for df format
# when wanting to plot elevation charts, can switch to a datetime index
