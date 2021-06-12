from pyquery import PyQuery as pq

import demjson
import pandas as pd
import re


RESPONSETIMES_PATTERN = re.compile(r'.*var stats_history ?= ?({[\S\s]*});.*', re.UNICODE)


def read_df_system(file, machine):
    # Read CSV data
    # Skip first row as it's useless
    # Only select the desired columns
    # Make sure #Date, Time columns are strings so we can easily parse them later
    df = pd.read_csv(file, skiprows = 1,
        usecols = ['#Date', 'Time', '[CPU]Totl%', '[MEM]Tot', '[MEM]Used', '[NET]RxKBTot', '[NET]TxKBTot'],
        dtype = {
            '#Date': str,
            'Time': str
        })

    # Build a time series with Timestamp objects from the #Date, Time columns
    timeseries = df[['#Date', 'Time']].apply(
        lambda s: pd.Timestamp(
            year = int(s[0][:4]),
            month = int(s[0][4:6]),
            day = int(s[0][6:]),
            hour = int(s[1].split(':')[0]),
            minute = int(s[1].split(':')[1]),
            second = int(s[1].split(':')[2])
        )
    , axis = 1)

    # Build a timedelta-based index
    test_start = timeseries.iloc[0]
    timeindex = timeseries.apply(lambda s: (s - test_start))

    df.index = pd.MultiIndex.from_product([[machine], timeindex], names = ['machine', 'time'])

    df.rename(columns = {
        '[CPU]Totl%': 'cpu_%',
        '[MEM]Tot': 'mem_total_kb',
        '[MEM]Used': 'mem_used_kb',
        '[NET]RxKBTot': 'net_recv_kb',
        '[NET]TxKBTot': 'net_send_kb'
    }, inplace = True)

    df.insert(4, 'mem_%', (df['mem_used_kb'] / df['mem_total_kb'] * 100).round().astype(int))

    df['net_recv_mb'] = df['net_recv_kb'] / 1000
    df['net_send_mb'] = df['net_send_kb'] / 1000

    df.drop(columns = ['#Date', 'Time', 'mem_total_kb', 'mem_used_kb', 'net_recv_kb', 'net_send_kb'], inplace = True)

    return df


def read_dfs_system(app, storage, test_name, test_size):
    df = read_df_system(f'{app.lower()}/{storage.lower()}/{test_name}_{test_size}/cloud74_{test_name}_{test_size}_system.csv', 'cloud74')
    
    for i in range(75, 77):
        df2 = read_df_system(f'{app.lower()}/{storage.lower()}/{test_name}_{test_size}/cloud{i}_{test_name}_{test_size}_system.csv', f'cloud{i}')

        df = df.append(df2)
    
    return df


def read_df_io(app, storage, test_name, test_size, machine):
    # Read CSV data
    # Skip first row as it's useless
    # Only select the desired columns
    # Make sure #Date, Time columns are strings so we can easily parse them later
    df = pd.read_csv(f'{app.lower()}/{storage.lower()}/{test_name}_{test_size}/{machine}_{test_name}_{test_size}_io.csv',
        skiprows = 1,
        usecols = ['#Date', 'Time', '[DSK]ReadKBTot', '[DSK]WriteKBTot'],
        dtype = {
            '#Date': str,
            'Time': str
        })

    # Build a time series with Timestamp objects from the #Date, Time columns
    timeseries = df[['#Date', 'Time']].apply(
        lambda s: pd.Timestamp(
            year = int(s[0][:4]),
            month = int(s[0][4:6]),
            day = int(s[0][6:]),
            hour = int(s[1].split(':')[0]),
            minute = int(s[1].split(':')[1]),
            second = int(s[1].split(':')[2])
        )
    , axis = 1)

    # Build a timedelta-based index
    test_start = timeseries.iloc[0]
    timeindex = timeseries.apply(lambda s: (s - test_start))

    df.index = pd.MultiIndex.from_product([[machine], timeindex], names = ['machine', 'time'])

    df.rename(columns = {
        '[DSK]ReadKBTot': 'read_kb',
        '[DSK]WriteKBTot': 'write_kb'
    }, inplace = True)

    df['read_mb'] = df['read_kb'] / 1024
    df['write_mb'] = df['write_kb'] / 1024

    df.drop(columns = ['#Date', 'Time', 'read_kb', 'write_kb'], inplace = True)

    return df


def read_dfs_io(app, storage, test_name, test_size):
    df = read_df_io(app, storage, test_name, test_size, 'cloud106')
    
    for i in range(107, 109):
        df2 = read_df_io(app, storage, test_name, test_size, f'cloud{i}')

        df = df.append(df2)
    
    return df


def read_df_reporthtml(app, storage, test_name, test_size):
    global RESPONSETIMES_PATTERN

    # Parse the report.html file for the data, since the CSV doesn't contain the data that we want
    filepath = f'{app.lower()}/{storage.lower()}/{test_name}_{test_size}/report.html'

    with open(filepath, encoding = 'utf8') as f:
        d = pq(f.read())
    
    matches = RESPONSETIMES_PATTERN.search(d('script')[1].text)

    data = demjson.decode(matches[1])

    # Parse the JSON into a dataframe
    df = pd.DataFrame(data)

    # Process the columns to extract the value from the column, ignoring the users per second as that's a separate column already in the dataframe
    for column in df.columns[1:]:
        df[column] = df[column].apply(lambda x: float(x['value']))
    
    # Build a time series with Timestamp objects from the time column
    timeseries = df['time'].apply(lambda s: pd.Timestamp(s))

    # Build a string index based on a timedelta-based index
    test_start = timeseries.iloc[0]
    timeindex = timeseries.apply(lambda s: str(s - test_start).replace('0 days ', ''))

    # Set new index and drop old column
    df.index = timeindex
    df.drop(columns = 'time', inplace = True)

    return df


def read_df_locustcsv(app, storage, test_name):
    df = None
    
    for test_size in [25, 50, 75, 100]:
        df2 = pd.read_csv(f'{app.lower()}/{storage.lower()}/{test_name}_{test_size}/locust_{test_name}_{test_size}_stats.csv')
        df2 = df2[df2['Name'] == 'Aggregated']
        df2 = df2[['Median Response Time', 'Requests/s']]

        df2.set_index('Median Response Time', inplace = True)

        if df is None:
            df = df2
        else:
            df = df.append(df2)
    
    df['Requests/s'] = round(df['Requests/s'], 2)
    df.index = round(df.reset_index()['Median Response Time'] / 1000, 3)

    return df
