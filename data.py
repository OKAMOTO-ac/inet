import streamlit as st
import csv
import os

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