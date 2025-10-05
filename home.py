import streamlit as st
import pandas as pd
import csv
import os

st.header('周辺のお祭り(地域行事)検索システム')

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


keyword = st.text_input(
    label="イベント名・キーワード検索",
    value="",
    placeholder="例：花火"
)
if keyword:
    st.write("入力されたキーワード：", keyword)

st.divider()

df = pd.read_csv('event_data.csv')

for index, row in df.iterrows():
    with st.container(border=True):
        st.markdown(f"#### {row['name']}")
        
        st.write(f"**日時:** {row['date']} {row['time']}")
        
        st.write(f"**詳細:** {row['detail']}")