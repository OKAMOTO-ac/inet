import streamlit as st
import sqlite3
import hashlib
st.set_page_config(
    page_title="基本情報登録・ログイン", # ブラウザのタイトルバーに表示されるタイトル
    # ページ設定でサイドバーのメインメニュー（≡）とページ一覧を非表示にする
    initial_sidebar_state="collapsed"
)
# 認証機能
conn = sqlite3.connect('database.db')
c = conn.cursor()
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
def create_user():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')
def add_user(username, password):
    # パスワードはハッシュ化して保存
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username, make_hashes(password)))
    conn.commit()
def login_user(username, password):
    # 入力パスワードをハッシュ化して検索
    hashed_input_password = make_hashes(password)
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username, hashed_input_password))
    data = c.fetchall()
    return data
# お試しアカウント情報の設定
TEST_USER = "123"
TEST_PASS = "111"
def main():
    st.title("基本情報登録")
    # 初期化（ログイン後の情報保持用）
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    # 既にログイン済みの場合はホーム画面へ自動遷移
    if st.session_state.authenticated:
        st.switch_page("pages/home.py") # ホーム画面へ遷移
    # メイン画面に「ログイン」タブと「サインアップ」タブを作成
    tab_login, tab_signup = st.tabs(["ログイン", "サインアップ"])
    with tab_login: # ログイン画面
        st.subheader("ログイン画面")
        username = st.text_input("ユーザー名を入力してください", key="login_user")
        password = st.text_input("パスワードを入力してください", type='password', key="login_pass")
        if st.button("ログイン", key="login_btn"):
            #お試しアカウントのチェック
            is_test_login = (username == TEST_USER and password == TEST_PASS)
            # DB認証、またはお試しログインが成功した場合
            if is_test_login:
                # お試しログイン成功
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"【お試しログイン】{username}さんでログインしました。ホーム画面へ移動します。")
                st.switch_page("pages/home.py")
            else:
                # DB登録ユーザーの認証を試みる
                create_user() # テーブル作成
                result = login_user(username, password)
                if result:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"{username}さんでログインしました。ホーム画面へ移動します。")
                    st.switch_page("pages/home.py")
                else:
                    st.warning("ユーザー名かパスワードが間違っています")
    with tab_signup: # サインアップ画面
        st.subheader("アカウントを作成")
        new_user = st.text_input("ユーザー名を入力してください", key="signup_user")
        new_age = st.text_input("年齢を入力してください", key="signup_age")
        new_gender = st.selectbox("性別を選択してください",
                                  ['未選択', '男性', '女性', 'その他'],
                                  key="signup_gender")
        new_password = st.text_input("パスワードを入力してください", type='password', key="signup_pass")
        if st.button("サインアップ", key="signup_btn"):
            create_user()
            add_user(new_user, new_password) # add_user内でハッシュ化される
            st.success("アカウントの作成に成功しました")
            st.info("ログイン画面からログインしてください")
if __name__ == '__main__':
    main()