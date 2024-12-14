#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import cdsapi
import netCDF4
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import os
from datetime import date, datetime, timedelta
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
#import pandas as pd
import numpy as np

import certifi
import ssl
import urllib3

# Create a custom context
ssl_context = ssl.create_default_context(cafile=certifi.where())
urllib3.util.ssl_.create_urllib3_context = lambda *args, **kwargs: ssl_context

################################################################################
# 設定値
################################################################################
# データ抽出期間
dt1 = datetime(2024, 10, 1, 0, 0, 0)
dt2 = datetime(2024, 10, 7, 0, 0, 0)

# データ抽出地点
address = '東京都'

################################################################################
# データ抽出期間を補正する関数
################################################################################
#def correct_dt(shortname, dt1, dt2):
def correct_dt(shortname, dt1, dt2, path, files):
    # ディレクトリを作成する
    #if not os.path.exists('./csv_'+str(shortname)):
    #    os.makedirs('./csv_'+str(shortname))
        
    #path = './csv_'+str(shortname)
    filelist = []
    #files = os.listdir(path)
    
    for filename in files:
        if os.path.isfile(os.path.join(path, filename)):
            filelist.append(filename)
    
    # データ取得開始日時
    if len(filelist) == 0:
        start = 'ERA5_'+str(format(dt1.year, '04'))+'-'+str(format(dt1.month, '02'))+'-'+str(format(dt1.day, '02'))+'T'+str(format(dt1.hour, '02'))+'_00_00_'+str(shortname)+'.csv'
    else:
        start = max(filelist)
    str_d1 = str(start[5:9])+str(start[10:12])+str(start[13:15])+str(start[16:18])
    
    # データ取得終了日時
    if datetime.now() - timedelta(7) > dt2:
        end = dt2
    else:
        end = datetime.now() - timedelta(7)
    str_d2 = end.strftime('%Y%m%d%H')
    
    # データ抽出期間を設定
    dt1 = datetime(int(str_d1[:4]), int(str_d1[4:6]), int(str_d1[6:8]), int(str_d1[8:]), 0, 0)
    dt2 = datetime(int(str_d2[:4]), int(str_d2[4:6]), int(str_d2[6:8]), int(str_d2[8:]), 0, 0)

    #return (dt1, dt2)

def correct_dt_single(shortname, dt1, dt2):
    if not os.path.exists('./csv_'+str(shortname)):
        os.makedirs('./csv_'+str(shortname))
        
    path = './csv_'+str(shortname)
    files = os.listdir(path)

    correct_dt(shortname, dt1, dt2, path, files)

    return (dt1, dt2)

def correct_dt_pressure(shortname, lev, dt1, dt2):
    if not os.path.exists('./csv_'+str(shortname)+'_'+str(int(float(lev)))):
        os.makedirs('./csv_'+str(shortname)+'_'+str(int(float(lev))))
        
    path = './csv_'+str(shortname)+'_'+str(int(float(lev)))
    files = os.listdir(path)

    correct_dt(shortname, dt1, dt2, path, files)

    return (dt1, dt2)

################################################################################
# 地名から緯度、経度を取得する関数
################################################################################
def get_lat_lon(address):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

################################################################################
# CSVファイルを生成する関数
################################################################################
def gen_csv_single(shortname, t, matrix):
    #with open('./csv_'+str(shortname)+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'.csv', mode='w', newline='') as file:
    #    writer = csv.writer(file)
    #    writer.writerow(matrix)
    with open('./csv_'+str(shortname)+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(matrix)

def gen_csv_pressure(shortname, t, lev, matrix):
    #with open('./csv_'+str(shortname)+'_'+str(int(float(lev)))+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'_'+str(int(float(lev)))+'.csv', mode='w', newline='') as file:
    #    writer = csv.writer(file)
    #    writer.writerow(matrix)
    with open('./csv_'+str(shortname)+'_'+str(int(float(lev)))+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'_'+str(int(float(lev)))+'.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(matrix)

################################################################################
# 「ERA5 hourly data on single levels from 1940 to present」からデータを抽出する関数
# https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
################################################################################
def reanalysis_era5_single_levels(name, shortname, lat, lon, dt1, dt2):
    # データ抽出期間を補正
    period = correct_dt_single(shortname, dt1, dt2)
    dt1 = period[0]
    dt2 = period[1]
    print(f'{shortname}: {dt1} - {dt2} ({lon}, {lat})')

    dt = dt1
    #t = []
    #value = []

    while dt <= dt2:
        print(str(name))
        print(dt)

        c.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': str(name),
                'year': str(dt.year),
                'month': str(dt.month),
                'day': str(dt.day),
                'time': str(dt.strftime('%H:%M')),
                #'area': [lat+0.1, lon-0.1, lat-0.1, lon+0.1],
                'format': 'netcdf'
            },
            'download.nc')

        ncfile = 'download.nc'

        try:
            with netCDF4.Dataset(ncfile) as ds:
                variable_data = ds.variables[str(shortname)]

                len_i = len(variable_data[0,:,0])
                len_j = len(variable_data[0,0,:])
                matrix = np.zeros((len_i, len_j))
                print(type(matrix))
                print(len(matrix))
                print(len(matrix[0]))
                for i in tqdm(range(len(variable_data[0,:,0]))):
                    for j in range(len(variable_data[0,0,:])):
                        #print(variable_data)
                        #print(f'Variable Name: {variable_data.name}')
                        #print(f'Dimensions: {variable_data.dimensions}')
                        #print(f'Shape: {variable_data.shape}')
                        #print(f'Units: {variable_data.units}')
                        
                        #data = variable_data[0,i,j].astype('float16')
                        data = variable_data[0,i,j]

                        #matrix[i, j] = data
                        matrix[i, j] = "{:.2f}".format(data)
                
                matrix = matrix.tolist()
                #print(matrix)
                gen_csv_single(str(shortname), str(dt), matrix)
        except IOError as e:
            print(f"ファイルを開けませんでした: {e}")
        except KeyError as e:
            print(f"指定された変数が見つかりません: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
    
        dt += delta

################################################################################
# 「ERA5 hourly data on pressure levels from 1940 to present」からデータを抽出する関数
# https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels
################################################################################
def reanalysis_era5_pressure_levels(name, shortname, lev, lat, lon, dt1, dt2):
    # データ抽出期間を補正
    period = correct_dt_pressure(shortname, lev, dt1, dt2)
    dt1 = period[0]
    dt2 = period[1]
    print(f'{shortname}: {dt1} - {dt2} ({lon}, {lat})')
    
    dt = dt1
    #t = []
    #value = []

    while dt <= dt2:
        print(str(name))
        print(dt)

        c.retrieve(
            'reanalysis-era5-pressure-levels',
            {
                'product_type': 'reanalysis',
                'variable': str(name),
                'year': str(dt.year),
                'month': str(dt.month),
                'day': str(dt.day),
                'time': str(dt.strftime('%H:%M')),
                #'pressure_level': str(lev),
                #'area': [lat+0.1, lon-0.1, lat-0.1, lon+0.1],
                'format': 'netcdf'
            },
            'download.nc')

        ncfile = 'download.nc'

        try:
            with netCDF4.Dataset(ncfile) as ds:
                variable_data = ds.variables[str(shortname)]
                
                len_i = len(variable_data[0,:,0,0])
                len_j = len(variable_data[0,0,:,0])
                len_k = len(variable_data[0,0,0,:])
                matrix = np.zeros((len_j, len_k))
                print(type(matrix))
                print(len(matrix))
                print(len(matrix[0]))
                for i in tqdm(range(len_i)):
                    for j in tqdm(range(len_j)):
                        for k in range(len_k):
                            #print(variable_data)
                            #print(f'Variable Name: {variable_data.name}')
                            #print(f'Dimensions: {variable_data.dimensions}')
                            #print(f'Shape: {variable_data.shape}')
                            #print(f'Units: {variable_data.units}')

                            #data = variable_data[0,i,j,k].astype('float16')
                            data = variable_data[0,i,j,k]
                            #print(data)

                            #matrix[j, k] = data
                            matrix[j, k] = "{:.2f}".format(data)
                    matrix = matrix.tolist()
                    #print(matrix)
                    gen_csv_pressure(str(shortname), str(dt), str(ds.variables['pressure_level'][i]), matrix)
        except IOError as e:
            print(f"ファイルを開けませんでした: {e}")
        except KeyError as e:
            print(f"指定された変数が見つかりません: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            
        dt += delta

################################################################################
# 変数
################################################################################
# 緯度、経度
coordinates = get_lat_lon(address)
lat = coordinates[0]
lon = coordinates[1]

# 圧力レベル
lev = 1000

# 時間間隔
delta = timedelta(hours=1)

# CDS API
#c = cdsapi.Client(verify=False)
c = cdsapi.Client(timeout=600)

################################################################################
# 各データをダウンロードしてCSVファイルを生成
################################################################################
#-------------------------------------------------------------------------------
# ERA5 hourly data on pressure levels from 1940 to present
#-------------------------------------------------------------------------------
# 気温 (K)
reanalysis_era5_pressure_levels('temperature', 't', lev, lat, lon, dt1, dt2)

# 相対湿度 (%RH)
reanalysis_era5_pressure_levels('relative_humidity', 'r', lev, lat, lon, dt1, dt2)

#-------------------------------------------------------------------------------
# ERA5 hourly data on single levels from 1940 to present
#-------------------------------------------------------------------------------
# 気圧 (Pa)
reanalysis_era5_single_levels('surface_pressure', 'sp', lat, lon, dt1, dt2)

# 風速 (m/s)
reanalysis_era5_single_levels('10m_u_component_of_wind', 'u10', lat, lon, dt1, dt2)
reanalysis_era5_single_levels('10m_v_component_of_wind', 'v10', lat, lon, dt1, dt2)

# 降水量 (m/h)
reanalysis_era5_single_levels('convective_precipitation', 'cp', lat, lon, dt1, dt2)

# 全天日射量 (J/m2)
reanalysis_era5_single_levels('surface_solar_radiation_downwards', 'ssrd', lat, lon, dt1, dt2)


# In[ ]:


import os
import pandas as pd
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import math

################################################################################
# CSVファイルを結合する関数
################################################################################
def combine_csv(shortname):
    # 生成されたCSVファイルを名前昇順で並び替える
    path = './csv_'+str(shortname)
    csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
    csv_files.sort()
    
    # データを結合したものをCSVファイルとして出力する
    result = []
    for file in csv_files[:]:
        df = pd.read_csv(os.path.join(path, file))
        result.append([df.columns[0], df.columns[1]])
    with open(str(shortname)+'.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(result)

################################################################################
# 気温 (degC)
################################################################################
# 元データの「短い名前」
shortname = 't'

# CSVファイルを結合する
combine_csv(shortname)

# 結合したCSVファイルを読み込む
df = pd.read_csv(str(shortname)+'.csv', names=['datetime', 'value'])

df['datetime'] = pd.to_datetime(df['datetime'])
df['value'] = df['value'].astype(float)

datetime = df['datetime']
value = df['value']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append(value[i] - 273.15)
df_temperature = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_temperature.columns = ['datetime', 'temperature']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(-50, 50)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('Temperature (degC)')
plt.savefig('temperature.png')
plt.show()

################################################################################
# 相対湿度 (%RH)
################################################################################
# 元データの「短い名前」
shortname = 'r'

# CSVファイルを結合する
combine_csv(shortname)

# 結合したCSVファイルを読み込む
df = pd.read_csv(str(shortname)+'.csv', names=['datetime', 'value'])

df['datetime'] = pd.to_datetime(df['datetime'])
df['value'] = df['value'].astype(float)

datetime = df['datetime']
value = df['value']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append(value[i])
df_relative_humidity = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_relative_humidity.columns = ['datetime', 'relative_humidity']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(0, 100)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('Relative Humidity (%RH)')
plt.savefig('relative_humidity.png')
plt.show()

################################################################################
# 気圧 (hPa)
################################################################################
# 元データの「短い名前」
shortname = 'sp'

# CSVファイルを結合する
combine_csv(shortname)

# 結合したCSVファイルを読み込む
df = pd.read_csv(str(shortname)+'.csv', names=['datetime', 'value'])

df['datetime'] = pd.to_datetime(df['datetime'])
df['value'] = df['value'].astype(float)

datetime = df['datetime']
value = df['value']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append(value[i] / 100)
df_pressure = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_pressure.columns = ['datetime', 'pressure']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(900, 1100)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('Pressure (hPa)')
plt.savefig('pressure.png')
plt.show()

################################################################################
# 風速 (m/s)
################################################################################
# 元データの「短い名前」
shortname1 = 'u10'
shortname2 = 'v10'

# CSVファイルを結合する
combine_csv(shortname1)
combine_csv(shortname2)

# 結合したCSVファイルを読み込む
df1 = pd.read_csv(str(shortname1)+'.csv', names=['datetime', 'value1'])
df2 = pd.read_csv(str(shortname2)+'.csv', names=['datetime', 'value2'])
df = pd.merge(df1, df2, on='datetime')

df['datetime'] = pd.to_datetime(df['datetime'])
df['value1'] = df['value1'].astype(float)
df['value2'] = df['value2'].astype(float)

datetime = df['datetime']
value1 = df['value1']
value2 = df['value2']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append((value1[i]**2 + value1[i]**2)**0.5)
df_wind_speed = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_wind_speed.columns = ['datetime', 'wind_speed']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(0, 30)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('Wind Speed (m/s)')
plt.savefig('wind_speed.png')
plt.show()

################################################################################
# 降水量 (mm/h)
################################################################################
# 元データの「短い名前」
shortname = 'cp'

# CSVファイルを結合する
combine_csv(shortname)

# 結合したCSVファイルを読み込む
df = pd.read_csv(str(shortname)+'.csv', names=['datetime', 'value'])

df['datetime'] = pd.to_datetime(df['datetime'])
df['value'] = df['value'].astype(float)

datetime = df['datetime']
value = df['value']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append(value[i] * 1000)
df_precipitation = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_precipitation.columns = ['datetime', 'precipitation']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(0, 30)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('Precipitation (mm/h)')
plt.savefig('precipitation.png')
plt.show()

################################################################################
# 全天日射量 (W/m2)
################################################################################
# 元データの「短い名前」
shortname = 'ssrd'

# CSVファイルを結合する
combine_csv(shortname)

# 結合したCSVファイルを読み込む
df = pd.read_csv(str(shortname)+'.csv', names=['datetime', 'value'])

df['datetime'] = pd.to_datetime(df['datetime'])
df['value'] = df['value'].astype(float)

datetime = df['datetime']
value = df['value']

# データを編集する
value_adj = []
for i in range(len(datetime)):
    value_adj.append(value[i]/3600)
df_ghi = pd.concat([datetime,  pd.Series(value_adj)], axis=1)
df_ghi.columns = ['datetime', 'ghi']

# グラフを生成する
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(datetime, value_adj)
plt.ylim(0, 1000)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=30)
plt.ylabel('GHI (W/m2)')
plt.savefig('ghi.png')
plt.show()

################################################################################
# 一括表示
################################################################################
# データフレームを統合する
df = df_temperature
#df = pd.merge(df, df_relative_humidity, on='datetime')
df = pd.merge(df, df_pressure, on='datetime')
df = pd.merge(df, df_wind_speed, on='datetime')
df = pd.merge(df, df_precipitation, on='datetime')
df = pd.merge(df, df_ghi, on='datetime')

# グラフを生成する
fig = plt.figure(figsize=(12, 6))
ax1 = fig.subplots()
ax2 = ax1.twinx()
ax1.plot(df['datetime'], df['temperature'], color='r', label='Tmperature (degC)', linewidth=0.5)
ax1.plot(df['datetime'], df['relative_humidity'], color='y', label='Relative Humidity (%RH)', linewidth=0.5)
ax2.plot(df['datetime'], df['pressure'], color='g', label='Pressure (hPa)', linewidth=0.5)
ax1.plot(df['datetime'], df['wind_speed'], color='c', label='Wind Speed (m/s)', linewidth=0.5)
ax1.plot(df['datetime'], df['precipitation'], color='b', label='Precipitation (mm/h)', linewidth=0.5)
ax2.plot(df['datetime'], df['ghi'], color='m', label='GHI (W/m2)', linewidth=0.5)
ax1.set_ylim(0, 100)
ax2.set_ylim(0, 1200)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#ax1.xaxis.set_major_locator(mdates.DayLocator())
#ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU))
ax1.xaxis.set_major_locator(mdates.MonthLocator())
fig.autofmt_xdate(rotation=30)
ax1.set_ylabel('Tmperature, Relative Humidity, Wind Speed, Precipitation')
ax2.set_ylabel('Pressure, GHI')
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
lines = lines_1 + lines_2
labels = labels_1 + labels_2
ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)
plt.savefig('total.png')
plt.show()


# In[ ]:




