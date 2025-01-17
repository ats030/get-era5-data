from datetime import date, datetime, timedelta

def setting():
    ################################################################################
    # 設定値
    ################################################################################
    # データ抽出期間
    dt1 = datetime(2024, 10, 1, 0, 0, 0)
    dt2 = datetime(2024, 10, 7, 0, 0, 0)

    # データ抽出地点
    address = '東京都'

    # 圧力レベル
    lev = 1000

    return dt1, dt2, address, lev