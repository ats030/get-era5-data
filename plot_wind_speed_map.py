import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from configure import configure

# 設定値を取得
dt1, dt2, lev, dir = configure()
name = 'wind speed'
shortname = 'wind_speed'
unit = 'm/s'
cmap = 'turbo'
vmin = 0
vmax = 50
vstep = 5

# データの読み込み
ds_u10 = xr.open_dataset(f"{dir}/nc_u10/ERA5_2024-01-01T00_00_00_u10.nc")
ds_v10 = xr.open_dataset(f"{dir}/nc_v10/ERA5_2024-01-01T00_00_00_v10.nc")
u10 = ds_u10['u10']
v10 = ds_v10['v10']

# 合成データの計算
data = np.sqrt(u10**2 + v10**2)

# 緯度・経度情報の取得
lons = ds_u10['longitude']
lats = ds_u10['latitude']

# プロット設定
plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# データのプロット
data_slice = data.sel(valid_time=data.valid_time[0])
plot = ax.contourf(lons, lats, data_slice, 
                            transform=ccrs.PlateCarree(),
                            cmap=cmap, 
                            levels=np.arange(vmin, vmax + 1, 1),
                            extend='both')

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
valid_time_str = data.valid_time[0].dt.strftime('%Y-%m-%d %H:%M:%S').values
plt.title(f"{valid_time_str} UTC")

# カラーバーの設定
cbar = plt.colorbar(plot, 
                    ax=ax, 
                    orientation='horizontal', 
                    pad=0.05, 
                    aspect=30)

levels = np.arange(vmin, vmax + vstep, vstep)
cbar.set_ticks(levels)
cbar.set_ticklabels([f'{t:.0f}' for t in levels])
cbar.set_label(f'{name.capitalize()} ({unit})')

# プロット保存用ディレクトリ作成
png_dir = f"{dir}/png_{shortname}"
os.makedirs(png_dir, exist_ok=True)

# プロット保存
png_path = f"{png_dir}/ERA5_2024-01-01T00_00_00_{shortname}.png"
plt.savefig(png_path, dpi=300, bbox_inches='tight')
print(f"プロットを {png_path} に保存しました。")

# プロットをクローズ
plt.close()
