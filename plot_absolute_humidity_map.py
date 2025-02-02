import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from configure import configure

# 設定値を取得
dt1, dt2, lev, dir = configure()
name = 'absolute humidity'
shortname = 'absolute_humidity'
unit = 'g/m3'
cmap = 'Blues'
vmin = 0
vmax = 30
vstep = 5

# データの読み込み
ds_t = xr.open_dataset(f"{dir}/nc_t/ERA5_2024-01-01T00_00_00_t.nc")
ds_r = xr.open_dataset(f"{dir}/nc_r/ERA5_2024-01-01T00_00_00_r.nc")
t = ds_t['t']
r = ds_r['r']

# 合成データの計算
data = 217 * (6.1078 * 10 ** (7.5 * (t - 273.15) / ((t - 273.15) + 237.3))) / ((t - 273.15) + 273.15) * r / 100

data = data.sel(valid_time=data.valid_time[0], pressure_level=data.pressure_level[0])

# 緯度・経度情報の取得
lons = ds_t['longitude']
lats = ds_t['latitude']

# プロット設定
plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# データのプロット
plot = ax.contourf(lons, lats, data, 
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
valid_time_str = data.valid_time.dt.strftime('%Y-%m-%d %H:%M:%S').values
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
cbar.set_label(f'{name.capitalize()} at {lev} hPa ({unit})')

# プロット保存用ディレクトリ作成
png_dir = f"{dir}/png_{shortname}"
os.makedirs(png_dir, exist_ok=True)

# プロット保存
png_path = f"{png_dir}/ERA5_2024-01-01T00_00_00_{shortname}.png"
plt.savefig(png_path, dpi=300, bbox_inches='tight')
print(f"プロットを {png_path} に保存しました。")

# プロットをクローズ
plt.close()
