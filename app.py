import streamlit as st
import requests
import json
import os
import urllib.parse # 👈 新增這個套件來修復圖片網址

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演助手", layout="wide", page_icon="🎬")

# --- 🔐 登入守門員 ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<br><br><h1 style='text-align: center;'>🔒 AI 導演助手 (VIP版)</h1>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            password = st.text_input("輸入啟用碼", type="password", label_visibility="collapsed")
            if st.button("🔓 解鎖進入", type="primary", use_container_width=True):
                if password == st.secrets["ACCESS_CODE"]:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ 啟用碼錯誤")
        st.stop()

check_password()

# ==============================================
# 主程式
# ==============================================

st.title("🎬 AI 導演：視覺分鏡助手")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ 請設定 GOOGLE_API_KEY")
    st.stop()

with st.sidebar:
    st.header("📝 影片設定")
    v_type = st.selectbox("類型", ["Vlog", "短影音 (Reels/TikTok)", "廣告", "微電影"])
    v_topic = st.text_input("主題", "台北 101 跨年煙火")
    v_dur = st.slider("長度", 1, 10, 3)
    v_desc = st.text_area("描述", "熱鬧、感動")
    btn = st.button("🚀 生成分鏡 + 圖片", type="primary")

def generate_content(key, topic, style, duration, desc):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    
    # 🔴 關鍵修改：強制 visual 欄位只輸出英文，避免亂碼
    prompt = f"""
    你是專業導演。請製作 Shot List：
    主題：{topic}, 風格：{style}, 長度：{duration}分, 描述：{desc}
    
    請回傳純 JSON 陣列。每個物件格式：
    {{
        "id": "1",
        "visual": "Detailed description of the scene in ENGLISH ONLY (for AI image generation). Include lighting, style, composition.", 
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
        else:
            return None
    except:
        return None

if btn:
    with st.spinner("🤖 AI 正在繪製分鏡圖 (手機網路可能需稍候)..."):
        shots = generate_content(api_key, v_topic, v_type, v_dur, v_desc)
        
        if shots:
            st.divider()
            for shot in shots:
                c1, c2 = st.columns([1, 1.5])
                
                with c1:
                    # 🔴 關鍵修復：使用標準 URL 編碼
                    try:
                        prompt_safe = urllib.parse.quote(shot['visual'])
                        # 加入 width/height 參數讓手機載入更快
                        img_url = f"https://image.pollinations.ai/prompt/{prompt_safe}?width=800&height=600&nologo=true&seed={shot['id']}"
                        st.image(img_url, use_container_width=True)
                    except:
                        st.warning("⚠️ 圖片載入失敗")
                
                with c2:
                    st.subheader(f"鏡頭 {shot['id']}")
                    st.info(f"🎥 **{shot['desc']}**")
                    st.caption(f"🔊 {shot['audio']}")
                    st.file_uploader(f"📹 開啟相機 ({shot['id']})", type=['mp4', 'mov'], key=shot['id'])
                
                st.divider()
        else:
            st.error("生成失敗，請再試一次。")
