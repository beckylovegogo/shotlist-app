import streamlit as st
import requests
import json
import os
import urllib.parse
import random

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演助手 (Pro版)", layout="wide", page_icon="🎬")

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

st.title("🎬 AI 導演：視覺分鏡助手 (Pro)")

# 讀取 API Key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ 請設定 GOOGLE_API_KEY")
    st.stop()

with st.sidebar:
    st.header("📝 影片設定")
    v_type = st.selectbox("影片類型", ["Vlog", "短影音 (Reels/TikTok)", "商業廣告", "微電影", "YouTube 長片"])
    v_topic = st.text_input("主題", "台北 101 跨年煙火")
    v_dur = st.slider("長度", 1, 10, 3)
    v_desc = st.text_area("描述", "熱鬧、感動、電影感")
    btn = st.button("🚀 生成分鏡 + 圖片", type="primary")

def generate_content(key, topic, style, duration, desc):
    # 🔴 改回 gemini-1.5-pro (寫作能力最強)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    
    # 🔴 優化 Prompt：強調「電影感」並限制生圖關鍵字長度
    prompt = f"""
    你是一位榮獲奧斯卡獎的專業電影導演。請為以下專案撰寫詳細的 Shot List：
    
    - 影片類型：{style}
    - 主題：{topic}
    - 內容描述：{desc}
    - 時長：{duration} 分鐘
    
    請針對每一個鏡頭，提供極度專業的指導。
    請回傳純 JSON 格式 (不要用 Markdown)。JSON 結構如下：
    [
      {{
        "id": "1",
        "shot_size": "景別 (例: 特寫 Close-up)",
        "angle": "運鏡 (例: 低角度仰拍 Low angle)",
        "duration": "時間 (例: 3s)",
        "visual_keywords": "請給出 3 到 5 個英文單字，用來描述畫面，用逗號分隔 (例: fireworks, night, crowd, cinematic)",
        "description": "詳細的畫面描述與動作指導 (繁體中文，請寫得生動、有畫面感)",
        "audio": "聲音與配樂指示"
      }}
    ]
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            # 清理格式
            text = text.replace("```json", "").replace("```", "").strip()
            # 嘗試解析 JSON
            return json.loads(text)
        else:
            st.error(f"API 回傳錯誤: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"解析錯誤: {e}")
        return None

if btn:
    with st.spinner("🎥 金牌導演正在構思劇本 (Pro 模型較慢請稍候)..."):
        shots = generate_content(api_key, v_topic, v_type, v_dur, v_desc)
        
        if shots:
            st.divider()
            for shot in shots:
                c1, c2 = st.columns([1, 1.5])
                
                with c1:
                    # 🔴 圖片修復：只用關鍵字生圖，網址超短，保證不破圖
                    try:
                        keywords = shot['visual_keywords']
                        # 加強畫質參數
                        keywords_safe = urllib.parse.quote(keywords)
                        seed = random.randint(0, 1000)
                        # 使用 Turbo 模型加速載入
                        img_url = f"https://image.pollinations.ai/prompt/{keywords_safe}?width=800&height=450&nologo=true&model=turbo&seed={seed}"
                        st.image(img_url, use_container_width=True)
                    except:
                        st.warning("(圖片載入失敗)")
                
                with c2:
                    # 標題包含豐富資訊
                    st.markdown(f"### 🎬 鏡頭 {shot['id']}")
                    
                    # 使用標籤顯示參數
                    st.markdown(f"""
                    <span style="background-color:#eee; padding:4px 8px; border-radius:4px; font-size:0.9em">📏 {shot['shot_size']}</span>
                    <span style="background-color:#eee; padding:4px 8px; border-radius:4px; font-size:0.9em">🔄 {shot['angle']}</span>
                    <span style="background-color:#eee; padding:4px 8px; border-radius:4px; font-size:0.9em">⏱️ {shot['duration']}</span>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"**🎥 畫面指導：**\n{shot['description']}")
                    st.caption(f"🔊 **聲音：** {shot['audio']}")
                    
                    # 相機按鈕
                    st.file_uploader(f"📹 拍攝 ({shot['id']})", type=['mp4', 'mov'], key=shot['id'])
                
                st.divider()
        else:
            st.error("生成失敗，請確認 API Key 權限。")
