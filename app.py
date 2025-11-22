import streamlit as st
import requests
import json
import os

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演助手", layout="wide", page_icon="🎬")

# --- 🔐 登入守門員 (密碼鎖機制) ---
def check_password():
    """檢查用戶是否輸入了正確的通行碼"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        # 顯示登入畫面
        st.markdown("<br><br><h1 style='text-align: center;'>🔒 AI 導演助手 (VIP版)</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>本服務為邀請制，請輸入您的啟用碼 (Access Code)</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            password = st.text_input("輸入啟用碼", type="password", label_visibility="collapsed")
            if st.button("🔓 解鎖進入", type="primary", use_container_width=True):
                # 比對 Secrets 裡的密碼
                if password == st.secrets["ACCESS_CODE"]:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ 啟用碼錯誤，請聯繫管理員取得權限。")
        st.stop() # 停止執行下面的程式

# 執行登入檢查
check_password()

# ==============================================
# 以下是登入成功後的主程式
# ==============================================

st.title("🎬 AI 導演：視覺分鏡助手")

# 讀取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ 系統未設定 API Key，請在 Secrets 中設定。")
    st.stop()

# --- 側邊欄 ---
with st.sidebar:
    st.success("✅ 已驗證 VIP 身份")
    if st.button("登出"):
        st.session_state["authenticated"] = False
        st.rerun()
    st.divider()
    
    st.header("📝 影片設定")
    v_type = st.selectbox("類型", ["Vlog", "短影音 (Reels/TikTok)", "廣告", "微電影"])
    v_topic = st.text_input("主題", "例如：台北 101 跨年煙火")
    v_dur = st.slider("長度", 1, 10, 3)
    v_desc = st.text_area("描述", "例如：熱鬧、感動、強調煙火")
    btn = st.button("🚀 生成分鏡 + 圖片", type="primary")

# --- AI 生成邏輯 ---
def generate_content(key, topic, style, duration, desc):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    你是專業導演。請製作 Shot List：
    主題：{topic}, 風格：{style}, 長度：{duration}分, 描述：{desc}
    
    請回傳純 JSON 陣列。格式：
    {{
        "id": "1",
        "visual": "英文畫面描述(用於生圖), 包含 lighting, style, composition", 
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

# --- 主畫面顯示 ---
if btn:
    with st.spinner("🤖 AI 導演正在繪製分鏡圖..."):
        shots = generate_content(api_key, v_topic, v_type, v_dur, v_desc)
        
        if shots:
            st.divider()
            for shot in shots:
                c1, c2 = st.columns([1, 1.5])
                
                # 左邊：AI 示意圖
                with c1:
                    img_prompt = shot['visual'].replace(" ", "%20")
                    st.image(f"https://image.pollinations.ai/prompt/{img_prompt}?nologo=true", use_container_width=True)
                
                # 右邊：文字 + 相機
                with c2:
                    st.subheader(f"鏡頭 {shot['id']}")
                    st.info(f"🎥 **{shot['desc']}**")
                    st.caption(f"🔊 {shot['audio']}")
                    
                    # 相機按鈕
                    st.file_uploader(f"📹 開啟相機 / 上傳 ({shot['id']})", type=['mp4', 'mov'], key=shot['id'])
                
                st.divider()
        else:
            st.error("生成失敗，請稍後再試。")
