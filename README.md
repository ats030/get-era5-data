# ERA5のデータを取得するサンプル

本プロジェクトは、ERA5の大気再解析データを収集するPythonのサンプルです。

## ERA5とは

## セットアップ方法

- PythonでERA5のデータを取得するための設定
    https://zenn.dev/ats030/articles/get-era5-data-in-python

## 取得するデータ

本プロジェクトでは、以下のデータを取得します。

- [ERA5 hourly data on pressure levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview)
    - Temperature at 1000 hPa (K)
    - Relative humidity at 1000 hPa (%)

- [ERA5 hourly data on single levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)
    - Surface pressure (Pa)
    - 10m u-component of wind (m/s)
    - 10m v-component of wind (m/s)
    - Convective precipitation (m)
    - Surface solar radiation downwards (J/m2)

## 生成するマップ

本プロジェクトでは、以下のデータをプロットしたマップを生成します。

- Temperature at 1000 hPa (°C)
- Relative humidity at 1000 hPa (%)
- Surface pressure (hPa)
- Convective precipitation (mm/h)
- Surface solar radiation downwards (W/m2)
- Temperature & Relative humidity at 1000 hPa -> Absolute humidity at 1000 hPa (g/m3)
- 10m u-component of wind & 10m v-component of wind -> Wind speed (m/s)

## サンプルコードの実行


uvで実行する場合。
```bash
uvx sh <プロジェクトディレクトリ>/run.sh
```

## ライセンス