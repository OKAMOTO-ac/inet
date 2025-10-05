import streamlit as st
import pandas as pd
import csv
import os
import ast

if 'likes' not in st.session_state:
    st.session_state.likes = []

st.header('周辺のお祭り(地域行事)検索システム')

col1, col2 = st.columns(2)
with col1:
    if st.button('my page'):
        st.write('my pageが押されました。')

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
        new_event_data = [event_name, str(event_tag), event_date, event_time, event_detail]
        
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'tag', 'date', 'time', 'detail'])
                writer.writerow(new_event_data)
        else:
            with open(file_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(new_event_data)
        st.success('イベントが追加されました')
        st.rerun()

with col2:
    if st.button('イベントを追加', key='add_event_dialog_button'):
        add_event()

keyword = st.text_input(
    label="イベント名・キーワード検索",
    value="",
    placeholder="例：花火"
)
if keyword:
    st.write("入力されたキーワード：", keyword)

st.divider()

page_selection = st.radio(
    '表示するページを選択してください',
    ('すべてのイベント', 'お気に入りのイベント'),
    horizontal=True
)

TAG_IMAGES = {
    '花火大会': 'images/花火大会.jpeg',
    '祭り': 'images/祭り.jpg',
    'コンサート': 'images/コンサート.jpg',
}
DEFAULT_IMAGE = 'images/default.jpg'

df = pd.read_csv(file_path)

if df.empty:
    st.info("イベントデータがありません。イベントを追加してください。")
else:
    df['tag_list'] = df['tag'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) and x.strip().startswith('[') else [])

    # --- 検索フィルタ ---
    if keyword:
        df_to_show = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        st.subheader(f"検索結果：{len(df_to_show)} 件")
    else:
        df_to_show = df

    if page_selection == 'お気に入りのイベント':
        liked_events = st.session_state.likes
        if not liked_events:
            st.info('お気に入りしたイベントはまだありません。')
            st.stop()
        df_to_show = df[df['name'].isin(liked_events)]

    for index, row in df_to_show.iterrows():
        with st.container(border=True):
            col_content, col_image = st.columns([3, 1])

            with col_content:
                st.markdown(f"#### {row['name']}")
                st.write(f"**日時:** {row['date']} {row['time']}")
                st.write(f"**詳細:** {row['detail']}")

                event_name = row['name']
                is_liked = event_name in st.session_state.likes
                button_text = '❤️ お気に入り' if is_liked else '🤍 '
                    
                if st.button(button_text, key=f"like_button_{index}"):
                    if is_liked:
                        st.session_state.likes.remove(event_name)
                    else:                            st.session_state.likes.append(event_name)
                    st.rerun()
                
            with col_image:
                image_path = DEFAULT_IMAGE
                tags_for_event = row['tag_list']
                    
                for tag in tags_for_event:
                    if tag in TAG_IMAGES:
                        image_path = TAG_IMAGES[tag]
                        break
                    
                if os.path.exists(image_path):
                    st.image(image_path, width=500)