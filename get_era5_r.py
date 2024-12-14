from setting import setting
from get_lat_lon import get_lat_lon
from get_era5 import ERA5

# 設定値を取得する関数
dt1, dt2, address, lev = setting()
print(f'{dt1}/{dt2}/{address}/{lev}')

# 座標を取得する関数
lat, lon = get_lat_lon()
print(f'{lat}/{lon}')

# ERA5からデータを取得する関数
ERA5()

################################################################################
# 各データをダウンロードしてCSVファイルを生成
################################################################################
#-------------------------------------------------------------------------------
# ERA5 hourly data on pressure levels from 1940 to present
#-------------------------------------------------------------------------------
# 気温 (K)
#ERA5.reanalysis_era5_pressure_levels('temperature', 't', lev, lat, lon, dt1, dt2)

# 相対湿度 (%RH)
ERA5.reanalysis_era5_pressure_levels('relative_humidity', 'r', lev, lat, lon, dt1, dt2)

#-------------------------------------------------------------------------------
# ERA5 hourly data on single levels from 1940 to present
#-------------------------------------------------------------------------------
# 気圧 (Pa)
#ERA5.reanalysis_era5_single_levels('surface_pressure', 'sp', lat, lon, dt1, dt2)

# 風速 (m/s)
#ERA5.reanalysis_era5_single_levels('10m_u_component_of_wind', 'u10', lat, lon, dt1, dt2)
#ERA5.reanalysis_era5_single_levels('10m_v_component_of_wind', 'v10', lat, lon, dt1, dt2)

# 降水量 (m/h)
#ERA5.reanalysis_era5_single_levels('convective_precipitation', 'cp', lat, lon, dt1, dt2)

# 全天日射量 (J/m2)
#ERA5.reanalysis_era5_single_levels('surface_solar_radiation_downwards', 'ssrd', lat, lon, dt1, dt2)