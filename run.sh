#!/bin/bash

# Ubuntuを更新する
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y

# ディレクトリ設定
script_dir="$(cd "$(dirname "$0")" && pwd)"
base_dir="$(dirname "$script_dir")"

# Pythonスクリプトを実行する
uv run "$base_dir/get-era5-data/get_era5_data.py"
uv run "$base_dir/get-era5-data/plot_map.py"
uv run "$base_dir/get-era5-data/plot_absolute_humidity_map.py"
uv run "$base_dir/get-era5-data/plot_wind_speed_map.py"