from geopy.geocoders import Nominatim

def get_lat_lon():
    ################################################################################
    # 設定値
    ################################################################################
    # データ抽出地点
    address = '東京都'

    ################################################################################
    # 地名から緯度、経度を取得する関数
    ################################################################################
    def get_lat_lon(address):
        geolocator = Nominatim(user_agent="geo_locator")
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    
    ################################################################################
    # 変数
    ################################################################################
    # 緯度、経度
    coordinates = get_lat_lon(address)
    lat = coordinates[0]
    lon = coordinates[1]

    return lat, lon