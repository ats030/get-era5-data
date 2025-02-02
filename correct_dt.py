import os
from datetime import date, datetime, timedelta

################################################################################
# データ抽出期間を取得する関数
################################################################################
def correct_dt(shortname, dt1, dt2, path, files):
    filelist = []
    
    for filename in files:
        if os.path.isfile(os.path.join(path, filename)):
            filelist.append(filename)
    
    # データ取得開始日時
    if len(filelist) == 0:
        start = 'ERA5_'+str(format(dt1.year, '04'))+'-'+str(format(dt1.month, '02'))+'-'+str(format(dt1.day, '02'))+'T'+str(format(dt1.hour, '02'))+'_00_00_'+str(shortname)+'.nc'
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