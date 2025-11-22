import streamlit as st
import requests
import json
import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

# ==========================================
# 🔴 您的 App 網址
# ==========================================
REDIRECT_URI = "https://shotlist-app-8mhp28xmzvoktfddpmgbfr.streamlit.app/"
# ==========================================

st.set_page_config(page_title="AI 導演助手", layout="wide", page_icon="🎬")

# --- 設定 Google 登入 (改為從 Secrets 讀取，最安全！) ---
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

if 'credentials' not in st.session_state:
    st.session_state['credentials'] = None

def get_flow():
    # 關鍵修改：不再讀取檔案，而是讀取 Streamlit Secrets
    # 我們手動構建 Google 需要的設定字典
    client_config = {
        "web": {
            "client_id": st.secrets["web"]["client_id"],
            "client_secret": st.secrets["web"]["client_secret"],
            "auth_uri": st.secrets["web"]["auth_uri"],
            "token_uri": st.secrets["web"]["token_uri"],
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow

# --- 登入流程邏輯 ---
def check_login():
    query_params = st.query_params
    code = query_params.get('code')
    
    if code and not st.session_state['credentials']:
        try:
            flow = get_flow()
            flow.fetch_token(code=code)
            st.session_state['credentials'] = flow.credentials
            st.query_params.clear()
        except Exception as e:
            st.error(f"登入失敗: {e}")

    if not st.session_state['credentials']:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>👋 歡迎來到 AI 導演助手</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>請登入以開始製作您的專業分鏡腳本</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f'''
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{authorization_url}" target="_self">
                        <button style="background-color: #4285F4; color: white; border: none; padding: 12px 24px; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold;">
                            🔵 Sign in with Google
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"系統設定錯誤：請檢查 Streamlit Secrets 設定。\n錯誤訊息: {e}")

# --- 主程式 (AI 功能) ---
def show_main_app():
    try:
        user_info_service = build('oauth2', 'v2', credentials=st.session_state['credentials'])
        user_info = user_info_service.userinfo().get().execute()
        user_name = user_info.get('given_name', 'User')
        user_pic = user_info.get('picture', '')
    except:
        user_name = "訪客"
        user_pic = ""
    
    with st.sidebar:
        if user_pic:
            st.image(user_pic, width=50)
        st.write(f"Hi, **{user_name}**")
        if st.button("登出"):
            st.session_state['credentials'] = None
            st.rerun()
        st.divider()
    
    st.title("🎬 AI 導演：視覺分鏡助手")
    
    # 從 Secrets 讀取 AI Key
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ 未設定 AI API Key")
        return

    with st.sidebar:
        st.header("📝 影片設定")
        v_type = st.selectbox("類型", ["Vlog", "短影音", "廣告", "微電影"])
        v_topic = st.text_input("主題", "台北 101 跨年煙火")
        v_dur = st.slider("長度", 1, 10, 3)
        v_desc = st.text_area("描述", "熱鬧、感動")
        btn = st.button("🚀 生成分鏡 + 圖片", type="primary")

    if btn:
        with st.spinner("🤖 AI 正在繪製分鏡圖..."):
            shots = generate_content(api_key, v_topic, v_type, v_dur, v_desc)
            if shots:
                st.divider()
                for shot in shots:
                    c1, c2 = st.columns([1, 1.5])
                    with c1:
                        img_prompt = shot['visual'].replace(" ", "%20")
                        st.image(f"https://image.pollinations.ai/prompt/{img_prompt}?nologo=true", use_container_width=True)
                    with c2:
                        st.subheader(f"鏡頭 {shot['id']}")
                        st.info(f"🎥 **{shot['desc']}**")
                        st.caption(f"🔊 {shot['audio']}")
                        st.file_uploader(f"📹 拍攝 ({shot['id']})", type=['mp4', 'mov'], key=shot['id'])
                    st.divider()

def generate_content(key, topic, style, duration, desc):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    prompt = f"""
    你是專業導演。請製作 Shot List：
    主題：{topic}, 風格：{style}, 長度：{duration}分, 描述：{desc}
    請回傳純 JSON 陣列。每個物件包含：
    {{
        "id": "1",
        "visual": "英文畫面描述(用於生圖)",
        "desc": "繁體中文拍攝指導",
        "audio": "聲音備註"
    }}
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
    except:
        return None

if __name__ == '__main__':
    check_login()
