import streamlit as st
import pandas as pd
import pydeck as pdk
import urllib.parse
import csv
import os
from geopy.geocoders import Nominatim # geopyをインポート
import folium
import requests

FILE_PATH = './event_data.csv'
COLS = ['name', 'location', 'date', 'lat', 'lon', 'address', 'tag', 'time', 'detail']

@st.cache_resource
def get_geolocator():
    
    # 識別用のuser_agent
    return Nominatim(user_agent="event_search_system_app")

def geocode_address(addr):
    #住所を緯度経度に変換
    geolocator = get_geolocator()
    try:
        # ジオコーディングを実行
        location = geolocator.geocode(addr, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        # 通信エラーやタイムアウトなどの場合は警告を表示
        st.warning(f"ジオコーディングに失敗しました。住所を確認してください: {e}")
    # 失敗した場合は地図に表示されないようNoneを返す
    return None, None

#データ読み込み 
@st.cache_data
def load_data():
    if not os.path.exists(FILE_PATH):
        init_data = {'name': ['倉吉打吹まつり', '淀川花火大会', '神戸ルミナリエ', '岡山桃太郎祭り'],
                     'location': ['鳥取', '大阪', '兵庫', '岡山'], 'date': ['2025/08/01', '2025/08/09', '2025/12/06', '2025/08/02'],
                     'lat': [35.4920, 34.7073, 34.6923, 34.6617], 'lon': [133.8242, 135.4851, 135.1916, 133.9180],
                     'address': ['鳥取県倉吉市湊町', '大阪府大阪市淀川区新北野', '兵庫県神戸市中央区加納町', '岡山県岡山市北区表町'],
                     'tag': ["['祭り']", "['花火大会']", "['イルミネーション']", "['祭り']"],
                     'time': ["18:00:00", "19:30:00", "17:30:00", "18:00:00"],
                     'detail': ['倉吉市の夏祭り', '関西最大級の花火大会', '冬の神戸を彩る光の祭典', '岡山の夏の風物詩']}
        pd.DataFrame(init_data).to_csv(FILE_PATH, index=False, encoding='utf-8')
        
    df = pd.read_csv(FILE_PATH)
    for col in ['lat', 'lon']:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
    return df.loc[:, df.columns.intersection(COLS)]


@st.dialog('イベント追加')
def add_event():
    st.write('イベントの詳細を追加してください')
    name = st.text_input('イベント名')
    addr = st.text_input('場所（住所）：地図表示のため正確に入力してください')
    tag = st.multiselect('イベントタグ', ['花火大会', '祭り', 'コンサート', 'その他'], default=['その他'])
    date = st.date_input('イベント日付')
    time = st.time_input('イベント時刻')
    detail = st.text_area('イベント詳細')

    if st.button('追加'):
        if not name or not addr:
            st.error("イベント名と場所は必須です。")
            return
        
        # geopyで座標を取得
        lat, lon = geocode_address(addr)

        if lat is None or lon is None:
             st.warning("この住所の座標が見つかりませんでした。イベントは追加されますが、地図には表示されません。")

        new_event = {'name': name, 'location': '', 'date': date.strftime('%Y/%m/%d'), 'lat': lat, 'lon': lon, 
                     'address': addr, 'tag': str(tag), 'time': str(time), 'detail': detail}
        
        row_data = [new_event.get(h, '') for h in COLS] 
        is_new_file = not os.path.exists(FILE_PATH)

        with open(FILE_PATH, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if is_new_file: writer.writerow(COLS)
            writer.writerow(row_data)

        st.success(f'イベント "{name}" が追加されました。')
        st.cache_data.clear()
        st.rerun()


st.header('周辺のお祭り(地域行事)検索システム')

df = load_data()


cols = st.columns(3)
with cols[0]:
    if st.button('my page'): st.write('my pageが押されました。')
with cols[1]:
    if st.button('お気に入り'): st.write('お気に入りが押されました。')
with cols[2]:
    if st.button('＋イベントを追加'): add_event()

keyword = st.text_input(label="イベント名・キーワード検索", value="", placeholder="例：花火")

# データフィルタリング
if keyword:
    filtered_df = df[df.apply(lambda row: any(keyword.lower() in str(row[col]).lower() 
                                               for col in ['name', 'location', 'address', 'tag']), axis=1)]
else:
    filtered_df = df

st.write("入力されたキーワード：", keyword)

#地図表示
st.subheader('イベントマップ')
map_df = filtered_df.dropna(subset=['lat', 'lon'])

# foliumで地図表示
# 現在地の取得
response = requests.get("https://ipinfo.io/json")
data = response.json()
loc = data['loc'].split(',')
user_lat, user_lon = float(loc[0]), float(loc[1])
# 東京の緯度経度をデフォルトに設定
DEFAULT_LAT = 35.6895
DEFAULT_LON = 139.6917

try:
    response = requests.get("https://ipinfo.io/json")
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    data = response.json()
    
    if 'loc' in data and data['loc']:
        loc = data['loc'].split(',')
        user_lat, user_lon = float(loc[0]), float(loc[1])
    else:
        # 'loc'キーがない場合、手動でエラーを発生させてexceptブロックに移行
        raise KeyError()
    # -------------------------------------------------

except (requests.exceptions.RequestException, KeyError, ValueError) as e:
    # ネットワークエラー、キーエラー、値エラーのいずれかが発生した場合
    st.write(f"位置情報の取得に失敗しました。デフォルトの場所を使います。")
    user_lat, user_lon = DEFAULT_LAT, DEFAULT_LON

# 地図の中央を設定
map_center = [user_lat, user_lon]
m = folium.Map(location=map_center, zoom_start=14)

folium.Marker(
        location=[user_lat, user_lon],
        popup="あなたの現在地",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

# 地図上にピンを立てる
for i, row in filtered_df.iterrows():
    name = row['name']
    addr = row['address'] if row['address'] else row['location']
    query = urllib.parse.quote_plus(f"{name} {addr}")
    url = f"https://www.google.com/maps/search/?api=1&query={query}"
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"イベント名：{row['name']}\n 日付：{row['date']}\n <a href='{url}' target='_blank'>Googleマップで場所を開く</a>",
        icon=folium.Icon(color="blue")
    ).add_to(m)

st.components.v1.html(m._repr_html_(), height=600)

# イベント一覧とリンク 
st.subheader('検索結果一覧')
st.dataframe(filtered_df.drop(columns=['lat', 'lon'], errors='ignore'), use_container_width=True) 



st.subheader('外部Googleマップ検索リンク')
for idx, row in filtered_df.iterrows():
    name = row['name']
    addr = row['address'] if row['address'] else row['location']
    query = urllib.parse.quote_plus(f"{name} {addr}")
    url = f"https://www.google.com/maps/search/?api=1&query={query}"
    st.markdown(f"**{name}**: <a href='{url}' target='_blank'>Googleマップで場所を開く</a>", unsafe_allow_html=True)