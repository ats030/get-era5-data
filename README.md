# ERA5のデータを取得するサンプル

本プロジェクトは、ERA5の大気再解析データを収集するPythonのサンプルです。

＃実行手順

### 事前準備

- uvのインストール
    - https://zenn.dev/ats030/articles/how-to-use-uv-on-ubuntu
- PythonでERA5のデータを取得するための設定
    - https://zenn.dev/ats030/articles/get-era5-data-in-python

### 設定ファイル

```configure.py```で、「データ抽出期間」や「プロジェクトディレクトリ」をお好みに合わせて設定してください。

### サンプルコードの実行

上記ファイルを生成するには、以下を実行します。

uvで実行する場合、```uv init```を実行したディレクトリで以下のコマンドを実行します。
```bash
uvx sh <プロジェクトディレクトリ>/run.sh
```

## 生成されるファイル

### 取得するデータ

本プロジェクトでは、以下のデータ（```.nc```ファイル）を取得します。

- [ERA5 hourly data on pressure levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview)
    - Temperature at 1000 hPa (K)
    - Relative humidity at 1000 hPa (%)

- [ERA5 hourly data on single levels from 1940 to present](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)
    - Surface pressure (Pa)
    - 10m u-component of wind (m/s)
    - 10m v-component of wind (m/s)
    - Convective precipitation (m)
    - Surface solar radiation downwards (J/m2)

### 生成するマップ

本プロジェクトでは、以下のデータをプロットしたマップ（```.png```ファイル）を生成します。

- 取得したデータ
    - Temperature at 1000 hPa (°C)
    - Relative humidity at 1000 hPa (%)
    - Surface pressure (hPa)
    - Convective precipitation (mm/h)
    - Surface solar radiation downwards (W/m2)
- 合成データ
    - Temperature & Relative humidity at 1000 hPa -> Absolute humidity at 1000 hPa (g/m3)
    - 10m u-component of wind & 10m v-component of wind -> Wind speed (m/s)