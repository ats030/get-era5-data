import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime, timedelta
from configure import configure

def plot_map(name, shortname, unit, cmap, vmin, vmax, vstep, extend):
    # 設定値を取得
    dt1, dt2, lev, dir = configure()

    path = str(dir)+'/nc_'+str(shortname)
    files = os.listdir(path)
    
    # プロット保存用ディレクトリ作成
    png_dir = f"{dir}/png_{shortname}"
    os.makedirs(png_dir, exist_ok=True)

    dt = dt1
    while dt <= dt2:
        print(f"{shortname} / {dt}")

        # ファイルパスを指定
        #nc_path = f"{dir}/nc_{shortname}/ERA5_2024-01-01T00_00_00_{shortname}.nc"
        nc_path = f"{dir}/nc_{shortname}/ERA5_{format(dt.year, '04')}-{format(dt.month, '02')}-{format(dt.day, '02')}T{format(dt.hour, '02')}_00_00_{shortname}.nc"
        #png_path = f"{png_dir}/ERA5_2024-01-01T00_00_00_{shortname}.png"
        png_path = f"{png_dir}/ERA5_{format(dt.year, '04')}-{format(dt.month, '02')}-{format(dt.day, '02')}T{format(dt.hour, '02')}_00_00_{shortname}.png"
                
        if (os.path.isfile(nc_path) is True) and (os.path.isfile(png_path) is False):
            # デバッグ用：ファイルパス情報
            print(f"検索中のファイルパス: {nc_path}")
            print(f"ディレクトリ存在: {os.path.exists(os.path.dirname(nc_path))}")
            
            # ディレクトリ内のファイル一覧
            #if os.path.exists(os.path.dirname(nc_path)):
            #    print("ディレクトリ内のファイル:")
            #    print(os.listdir(os.path.dirname(nc_path)))

            try:
                # ファイルの存在確認
                if not os.path.exists(nc_path):
                    raise FileNotFoundError(f"ファイルが見つかりません: {nc_path}")

                # NetCDFデータの読み込み
                dataset = xr.open_dataset(nc_path)
                print(dataset)

                # データの選択
                data = dataset[shortname]
                if shortname == 't': data = data - 273.15  # K → °C
                elif shortname == 'r': data = data  # %RH
                elif shortname == 'sp': data = data * 0.01  # Pa → hPa
                elif shortname == 'u10': data = data  # m/s
                elif shortname == 'v10': data = data  # m/s
                elif shortname == 'cp': data = data * 1000  # m/h → mm/h
                #elif shortname == 'ssrd': data = data # W/m2
                elif shortname == 'ssrd': data = data / 3600  # J/m² → W/m²

                if shortname in ['t', 'r']:
                    data = data.sel(valid_time=data.valid_time[0], pressure_level=data.pressure_level[0])
                    if extend == 'neither':
                        data = data.clip(min=vmin, max=vmax)
                    elif extend == 'min':
                        data = data.clip(max=vmax)
                    elif extend == 'max':
                        data = data.clip(min=vmin)
                else:
                    pass

                # 緯度・経度情報の取得
                lons = dataset['longitude']
                lats = dataset['latitude']

                # プロット設定
                plt.figure(figsize=(15, 10))
                ax = plt.axes(projection=ccrs.PlateCarree())
                ax.set_global()

                # データのプロット
                if shortname in ['t', 'r']:
                    plot = ax.contourf(lons, lats, data, 
                                transform=ccrs.PlateCarree(),
                                cmap=cmap, 
                                levels=np.arange(vmin, vmax + 1, 1),
                                extend=extend)
                else:
                    data_slice = data.sel(valid_time=data.valid_time[0])
                    plot = ax.contourf(lons, lats, data_slice, 
                                    transform=ccrs.PlateCarree(),
                                    cmap=cmap, 
                                    levels=np.arange(vmin, vmax + 1, 1),
                                    extend=extend)

                # 地図要素の追加
                ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
                ax.add_feature(cfeature.LAKES.with_scale('110m'), linewidth=0.1, facecolor='none', edgecolor='black')
                ax.add_feature(cfeature.LAKES.with_scale('50m'), linewidth=0.1, facecolor='none', edgecolor='black')
                ax.add_feature(cfeature.RIVERS.with_scale('110m'), linewidth=0.1, edgecolor='black')
                ax.add_feature(cfeature.RIVERS.with_scale('50m'), linewidth=0.1, edgecolor='black')
                ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
                ax.gridlines(draw_labels=True, 
                            linewidth=0.5, 
                            color='gray', 
                            alpha=0.5, 
                            linestyle='--')

                # タイトルの設定
                if shortname in ['t', 'r']:
                    valid_time_str = data.valid_time.dt.strftime('%Y-%m-%d %H:%M:%S').values
                    #plt.title(f"{name.capitalize()} at {lev} hPa / {valid_time_str} UTC")
                    plt.title(f"{valid_time_str} UTC")
                else:
                    valid_time_str = data.valid_time[0].dt.strftime('%Y-%m-%d %H:%M:%S').values
                    #plt.title(f"{name.capitalize()} / {valid_time_str} UTC")
                    plt.title(f"{valid_time_str} UTC")

                # カラーバーの設定
                cbar = plt.colorbar(plot, 
                            ax=ax, 
                            orientation='horizontal', 
                            pad=0.05, 
                            aspect=30,
                            extend=extend) 
                
                levels = np.arange(vmin, vmax + vstep, vstep)
                cbar.set_ticks(levels)
                cbar.set_ticklabels([f'{t:.0f}' for t in levels])
                #cbar.set_label(f'{shortname} ({unit})')
                if shortname in ['t', 'r']:
                    cbar.set_label(f'{name.capitalize()} at {lev} hPa ({unit})')
                else:
                    cbar.set_label(f'{name.capitalize()}  ({unit})')

                # プロット保存
                plt.savefig(png_path, dpi=300, bbox_inches='tight')
                print(f"プロットを {png_path} に保存しました。")

                # プロットをクローズ
                plt.close()

            except FileNotFoundError as e:
                print(f"ファイルエラー: {e}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
        else:
            pass

        dt = dt + timedelta(hours=1)

if __name__ == "__main__":
    # 気温 (°C)
    plot_map('temperature', 't', '°C', cmap='RdBu_r', vmin=-40, vmax=40, vstep=10, extend='both')
    
    '''# 相対湿度 (%RH)
    plot_map('relative humidity', 'r', '%', cmap='Blues', vmin=0, vmax=100, vstep=10, extend='neither')

    # 気圧 (hPa)
    plot_map('surface pressure', 'sp', 'hPa', cmap='gist_earth_r', vmin=500, vmax=1100, vstep=50, extend='both')

    # 風速 (m/s)
    plot_map('10m u-component of wind', 'u10', 'm/s', cmap='RdBu_r', vmin=-50, vmax=50, vstep=10, extend='both')
    plot_map('10m v-component of wind', 'v10', 'm/s', cmap='RdBu_r', vmin=-50, vmax=50, vstep=10, extend='both')

    # 降水量 (mm/h)
    plot_map('convective precipitation', 'cp', 'mm/h', cmap='Blues', vmin=0, vmax=10, vstep=1, extend='max')

    # 全天日射量 (W/m2)
    plot_map('surface solar radiation downwards', 'ssrd', 'W/m2', cmap='hot', vmin=0, vmax=1200, vstep=100, extend='max')'''