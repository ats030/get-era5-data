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

class ERA5():
    # Create a custom context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    urllib3.util.ssl_.create_urllib3_context = lambda *args, **kwargs: ERA5.ssl_context

    ################################################################################
    # データ抽出期間を補正する関数
    ################################################################################
    def correct_dt(shortname, dt1, dt2, path, files):
        filelist = []
        
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

        ERA5.correct_dt(shortname, dt1, dt2, path, files)

        return (dt1, dt2)

    def correct_dt_pressure(shortname, lev, dt1, dt2):
        if not os.path.exists('./csv_'+str(shortname)+'_'+str(int(float(lev)))):
            os.makedirs('./csv_'+str(shortname)+'_'+str(int(float(lev))))
            
        path = './csv_'+str(shortname)+'_'+str(int(float(lev)))
        files = os.listdir(path)

        ERA5.correct_dt(shortname, dt1, dt2, path, files)

        return (dt1, dt2)

    ################################################################################
    # CSVファイルを生成する関数
    ################################################################################
    def gen_csv_single(shortname, t, matrix):
        with open('./csv_'+str(shortname)+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'.csv', mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(matrix)

    def gen_csv_pressure(shortname, t, lev, matrix):
        with open('./csv_'+str(shortname)+'_'+str(int(float(lev)))+'/ERA5_'+str(t[:10])+'T'+str(t[11:13])+'_00_00_'+str(shortname)+'_'+str(int(float(lev)))+'.csv', mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(matrix)

    ################################################################################
    # 「ERA5 hourly data on single levels from 1940 to present」からデータを抽出する関数
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
    ################################################################################
    def reanalysis_era5_single_levels(name, shortname, lat, lon, dt1, dt2):
        # データ抽出期間を補正
        period = ERA5.correct_dt_single(shortname, dt1, dt2)
        dt1 = period[0]
        dt2 = period[1]
        print(f'{shortname}: {dt1} - {dt2} ({lon}, {lat})')

        dt = dt1

        while dt <= dt2:
            print(str(name))
            print(dt)

            ERA5.c.retrieve(
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
                'download_'+str(shortname)+'.nc')

            ncfile = 'download_'+str(shortname)+'.nc'

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
                            
                            data = variable_data[0,i,j]

                            matrix[i, j] = "{:.2f}".format(data)
                    
                    matrix = matrix.tolist()
                    #print(matrix)
                    ERA5.gen_csv_single(str(shortname), str(dt), matrix)
            except IOError as e:
                print(f"ファイルを開けませんでした: {e}")
            except KeyError as e:
                print(f"指定された変数が見つかりません: {e}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
        
            dt += ERA5.delta

    ################################################################################
    # 「ERA5 hourly data on pressure levels from 1940 to present」からデータを抽出する関数
    # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels
    ################################################################################
    def reanalysis_era5_pressure_levels(name, shortname, lev, lat, lon, dt1, dt2):
        # データ抽出期間を補正
        period = ERA5.correct_dt_pressure(shortname, lev, dt1, dt2)
        dt1 = period[0]
        dt2 = period[1]
        print(f'{shortname}: {dt1} - {dt2} ({lon}, {lat})')
        
        dt = dt1

        while dt <= dt2:
            print(str(name))
            print(dt)

            ERA5.c.retrieve(
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
                'download_'+str(shortname)+'.nc')

            ncfile = 'download_'+str(shortname)+'.nc'

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

                                data = variable_data[0,i,j,k]

                                matrix[j, k] = "{:.2f}".format(data)
                        matrix = matrix.tolist()
                        #print(matrix)
                        ERA5.gen_csv_pressure(str(shortname), str(dt), str(ds.variables['pressure_level'][i]), matrix)
            except IOError as e:
                print(f"ファイルを開けませんでした: {e}")
            except KeyError as e:
                print(f"指定された変数が見つかりません: {e}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
                
            dt += ERA5.delta

    ################################################################################
    # 変数
    ################################################################################
    # 時間間隔
    delta = timedelta(hours=1)

    # CDS API
    #c = cdsapi.Client(verify=False)
    c = cdsapi.Client(timeout=600)