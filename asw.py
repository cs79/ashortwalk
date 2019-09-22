import pandas as pd
import os, gpxpy
import matplotlib.pyplot as plt
# matplotlib qt

gpx_dir_path = 'C:/users/cloud/Dropbox/Projects/ashortwalk/gpxdata'
os.chdir(gpx_dir_path)

def parse_gpx(gpx_file_path):
    '''
    '''
    gpx_file = open(gpx_file_path)
    gpx = gpxpy.parse(gpx_file)
    return(gpx)

# as a lambda:
parse_gpx = lambda x: gpxpy.parse(open(x, 'r'))

# figure out what all is in these things:
track = parse_gpx('GAIA_Dushanbe_to_Khorog_8_4_19_5_21_57_AM.gpx')
pts = track.get_points_data()

# stuff that will wind up in a loop:
pt = pts[0][0]

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
