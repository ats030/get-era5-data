from datetime import date, datetime, timedelta

def configure():
    ################################################################################
    # 設定値
    ################################################################################
    # データ抽出期間
    #dt1 = datetime(1940, 1, 1, 0, 0, 0)
    dt1 = datetime(2024, 1, 1, 0, 0, 0)
    dt2 = datetime.now()

    # 圧力レベル
    lev = 1000

    # ディレクトリ
    dir = '/home/ats030/pCloudDrive/Python/get-era5-data'

    return dt1, dt2, lev, dir
