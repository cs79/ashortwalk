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
# day1track = parse_gpx('GAIA_Dushanbe_to_Khorog_8_4_19_5_21_57_AM.gpx')
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
# also for days 2-5, fix dist_from_start to correct for the split
td1 = f5df.loc[0:candidate_eods[1],:]
td2 = f5df.loc[candidate_eods[1]+1:candidate_eods[3],:]
td2['dist_from_start'] = [i - td2.loc[td2.index[0], 'dist_from_start'] for i in td2['dist_from_start']]
td3 = f5df.loc[candidate_eods[3]+1:candidate_eods[5],:]
td3['dist_from_start'] = [i - td3.loc[td3.index[0], 'dist_from_start'] for i in td3['dist_from_start']]
td4 = f5df.loc[candidate_eods[5]+1:candidate_eods[7],:]
td4['dist_from_start'] = [i - td4.loc[td4.index[0], 'dist_from_start'] for i in td4['dist_from_start']]
td5 = f5df.loc[candidate_eods[7]+1:f5df.index[-1],:]
td5['dist_from_start'] = [i - td5.loc[td5.index[0], 'dist_from_start'] for i in td5['dist_from_start']]
# no td6 - stuck at Kyrgyz settlement
td7 = summarize_points(day7)
td8 = summarize_points(day8)
td9 = summarize_points(day9)
td10 = summarize_points(day10)
td11_partial = summarize_points(day11_partial)

# NEED TO OFFSET dist_from_start FOR ALL DAYS IN COMBINED DATA
# for each day after day 1, add tail(0) dist_from_start value from previous day
# to all points in that day
td1['total_dist'] = td1['dist_from_start']
td2['total_dist'] = td2['dist_from_start'] + td1['total_dist'].values[-1]
td3['total_dist'] = td3['dist_from_start'] + td2['total_dist'].values[-1]
td4['total_dist'] = td4['dist_from_start'] + td3['total_dist'].values[-1]
td5['total_dist'] = td5['dist_from_start'] + td4['total_dist'].values[-1]
td7['total_dist'] = td7['dist_from_start'] + td5['total_dist'].values[-1]
td8['total_dist'] = td8['dist_from_start'] + td7['total_dist'].values[-1]
td9['total_dist'] = td9['dist_from_start'] + td8['total_dist'].values[-1]
td10['total_dist'] = td10['dist_from_start'] + td9['total_dist'].values[-1]
td11_partial['total_dist'] = td11_partial['dist_from_start'] + \
                             td10['total_dist'].values[-1]

combined_distance_track_data = td1
for d in [td2, td3, td4, td5, td7, td8, td9, td10, td11_partial]:
    combined_distance_track_data.append(d)
combined_distance_track_data.to_csv('../combined_distance_track_data.csv')

# pack these into a dict for ease of access later:
trekdata = {1: td1,
            2: td2,
            3: td3,
            4: td4,
            5: td5,
            7: td7,
            8: td8,
            9: td9,
            10: td10,
            11: td11_partial}

# summarize each day (distance, elevation +/-/net, elapsed time)
def summarize_day(df):
    '''
    Given a dataframe of summarized GPX point data, calculate stats on:
    - Distance traveled
    - Time elapsed
    - Gross elevation gain
    - Gross elevation loss
    - Net daily elevation change (end - start)
    - Elevation spread (max - min)
    '''
    # reindex just in case
    df.sort_values('datetime', inplace=True)
    df.index = range(len(df))
    # get the elevation diffs
    df['elevation_diff'] = df['elevation'].diff(1)
    # calculate various stats for the day assuming sorted
    to_return = {'distance': df['dist_from_start'].values[-1],
                 'time_elapsed': pd.Timedelta(df['datetime'].values[-1] - df['datetime'].values[0]).seconds,
                 'elev_delta_GROSS_POS': sum([i for i in df['elevation_diff'] if i > 0]),
                 'elev_delta_GROSS_NEG': sum([i for i in df['elevation_diff'] if i < 0]),
                 'elev_delta_DAILY_NET': df['elevation'].values[-1] - df['elevation'].values[0],
                 'elev_delta_SPREAD': df['elevation'].max() - df['elevation'].min()}
    return(to_return)

daily_summaries = pd.DataFrame(columns=['distance', 'time_elapsed', 'elev_delta_GROSS_POS', 'elev_delta_GROSS_NEG', 'elev_delta_DAILY_NET', 'elev_delta_SPREAD'])
for i in range(1, 12):
    if i == 6:
        continue
    ds = summarize_day(trekdata[i])
    daily_summaries.loc['Day {}'.format(i), 'distance'] = ds['distance']
    daily_summaries.loc['Day {}'.format(i), 'time_elapsed'] = ds['time_elapsed']
    daily_summaries.loc['Day {}'.format(i), 'elev_delta_GROSS_POS'] = ds['elev_delta_GROSS_POS']
    daily_summaries.loc['Day {}'.format(i), 'elev_delta_GROSS_NEG'] = ds['elev_delta_GROSS_NEG']
    daily_summaries.loc['Day {}'.format(i), 'elev_delta_DAILY_NET'] = ds['elev_delta_DAILY_NET']
    daily_summaries.loc['Day {}'.format(i), 'elev_delta_SPREAD'] = ds['elev_delta_SPREAD']
daily_summaries.to_csv('../daily_summary_stats.csv')

# also get a "full trek" altitude profile; i guess assume even spacing of pts?
# this actually is no good because the distances for non-f5df dfs are not cumulative
combined = pd.DataFrame(columns=td1.columns)
for df in (f5df, td7, td8, td9, td10, td11_partial):
    combined = combined.append(df)
combined.index = range(len(combined))
combined.to_csv('../combined_track_data.csv')
# combined['elevation'].plot()
# plt.show()

# additional modifications to the full trek file
df = pd.read_csv('combined_distance_track_data.csv', index_col=0)
df['day'] = [pd.to_datetime(df['datetime'].values[i]).day for i in range(len(df))]
df2 = pd.DataFrame()
days = list(set(df['day']))
days.sort()
for d in days:
    subset = df[df['day'] == d]
    dist = subset['total_dist'] - subset['total_dist'].values[0] # offset for day
    df2 = df2.append(dist.to_frame())
df2.index = df.index
df['daily_dist'] = df2['total_dist']
df.index = range(len(df))
df.to_csv('combined_distance_track_data_w_daily_distance.csv')
# km by day
kmpd = df.groupby('day')['daily_dist'].max() / 1000
# miles by day
mpd = kmpd * 0.621371
# time by day
times = pd.DataFrame()
for d in days:
    subset = df[df['day'] == d]
    timediff = pd.to_datetime(subset['datetime'].values[-1]) - \
               pd.to_datetime(subset['datetime'].values[0])
    times.loc[d, 'elapsed_time'] = timediff

# attempt to find correct date ends
df['dt'] = [pd.to_datetime(i) for i in df['datetime']]
df['td'] = df['dt'].diff(1)

df3 = df.copy()
df3.set_index('dt', inplace=True)
df3.index = df3.index.tz_convert('Asia/Kabul')
df3.drop(['day', 'daily_dist', 'td'], axis=1, inplace=True)
df3['day'] = [i.day for i in df3.index]
df3['dt'] = df3.index
df3['td'] = df3['dt'].diff(1)
df3['td'] = [i.seconds for i in df3['td']]
df3.index = range(len(df3))
# manual day fix
df3.loc[0:4130, 'corrected_day'] = 1
df3.loc[4131:8045, 'corrected_day'] = 2
df3.loc[8046:14337, 'corrected_day'] = 3
df3.loc[14338:16165, 'corrected_day'] = 4
df3.loc[16166:20690, 'corrected_day'] = 5
df3.loc[20691:24219, 'corrected_day'] = 7
df3.loc[24220:27514, 'corrected_day'] = 8
df3.loc[27515:33030, 'corrected_day'] = 9
df3.loc[33031:35619, 'corrected_day'] = 10
df3.loc[35620:39213, 'corrected_day'] = 11

df4 = pd.DataFrame()
days2 = list(set(df3['corrected_day']))
days2.sort()
for d in days2:
    subset = df3[df3['corrected_day'] == d]
    dist = subset['total_dist'] - subset['total_dist'].values[0] # offset for day
    df4 = df4.append(dist.to_frame())
df4.index = df3.index
df3['daily_dist'] = df4['total_dist']
df3.index = range(len(df3))
#df3.to_csv('combined_distance_track_data_w_daily_distance_CORRECTED_DAYS.csv')
# km by day
kmpd = df3.groupby('corrected_day')['daily_dist'].max() / 1000
# miles by day
mpd = kmpd * 0.621371
# time by day
times = pd.DataFrame()
for d in days2:
    subset = df3[df3['corrected_day'] == d]
    timediff = subset['dt'].values[-1] - subset['dt'].values[0]
    times.loc[d, 'elapsed_time'] = timediff

kmpd.to_csv('km_per_day_CORRECTED.csv')
mpd.to_csv('miles_per_day_CORRECTED.csv')
times.to_csv('times_per_day_CORRECTED.csv')

# additional stats for book; assuming df is corrected full track data
elevation_gain = max(df['elevation']) - df.loc[0, 'elevation']
elevation_delta = max(df['elevation']) - min(df['elevation'])
daily_elevation_deltas = df.groupby('corrected_day')['elevation'].max() - \
                         df.groupby('corrected_day')['elevation'].min()
daily_elevation_gains = []
daily_elevation_losses = []
for d in set(df['corrected_day']):
    subset = df[df['corrected_day'] == d]
    delta_g = subset['elevation'].max() - subset.loc[subset.index.values[0], 'elevation']
    delta_l = subset.loc[subset.index.values[0], 'elevation'] - subset['elevation'].min()
    daily_elevation_gains.append(delta_g)
    daily_elevation_losses.append(delta_l)
max_daily_elevation_delta = daily_elevation_deltas.max()
max_daily_elevation_gain = max(daily_elevation_gains)
max_daily_elevation_loss = max(daily_elevation_losses)
'''
Other stats:
Total waypoints logged manually: 98
"River crossing" waypoints logged: 21
"River crossing by animal" waypoints logged: 5
'''
