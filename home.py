import streamlit as st
import pandas as pd
import csv
import os
import datetime

st.header('周辺のお祭り(地域行事)検索システム')

df = pd.read_csv('event_data.csv')

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('my page'):
        st.write('my pageが押されました。')
with col2:
    if st.button('お気に入り'):
        st.write('お気に入りが押されました。')
with col3:
    if st.button('＋イベントを追加'):
        st.write('イベントを追加が押されました。')

file_path = './event_data.csv'

@st.dialog('イベント追加')
def add_event():
    st.write('イベントの詳細を追加してください')
    event_name = st.text_input('イベント名')
    event_tag = st.multiselect('イベントタグ', ['花火大会', '祭り', 'コンサート'])
    event_date = st.date_input('イベント日付')
    event_time = st.time_input('イベント時刻')
    event_detail = st.text_area('イベント詳細')
    if st.button('追加'):
        st.success('イベントが追加されました')
        st.session_state.yourevent = {'name': event_name, 'tag': event_tag, 'date': event_date, 'time': event_time, 'detail': event_detail}
        
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'tag', 'date', 'time', 'detail'])
                writer.writerow([st.session_state.yourevent['name'], st.session_state.yourevent['tag'], st.session_state.yourevent['date'], st.session_state.yourevent['time'], st.session_state.yourevent['detail']])

        else:
            with open(file_path, 'a', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([st.session_state.yourevent['name'], st.session_state.yourevent['tag'], st.session_state.yourevent['date'], st.session_state.yourevent['time'], st.session_state.yourevent['detail']])
        
        st.rerun()


if st.button('イベントを追加'):
    add_event()
    st.session_state.yourevent = None
    # st.success('イベントが追加されました')

col1, col2, = st.columns([3,1])
with col1:
    keyword = st.text_input(
    label="イベント名・キーワード検索",
    value="",
    placeholder="例：花火"
    )
    if keyword:
        st.write("入力されたキーワード：", keyword)
with col2:
    tag = st.selectbox(
        "",
        ["タグを選択", '花火大会', '祭り', 'コンサート'],
        # label_visibility="collapsed"
    )
# with col3:
#     search_btn = st.button("検索")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("開始日", value=pd.to_datetime(df['date']).min())
with col2:
    end_date = st.date_input("終了日", value=pd.to_datetime(df['date']).max())

st.divider()

# --- 検索フィルタ ---
filtered_df = df
## --- キーワード検索 ---
if keyword:
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
## --- タグ検索 ---
if tag != "タグを選択":
    filtered_df = filtered_df[filtered_df['tag'].apply(lambda x: tag in x)]
## --- 日付検索 ---
filtered_df = filtered_df[
    (pd.to_datetime(filtered_df['date']) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(filtered_df['date']) <= pd.to_datetime(end_date))
]
st.subheader(f"検索結果：{len(filtered_df)} 件")

for index, row in filtered_df.iterrows():
    with st.container(border=True):
        st.markdown(f"#### {row['name']}")
        
        st.write(f"**日時:** {row['date']} {row['time']}")
        
        st.write(f"**詳細:** {row['detail']}")