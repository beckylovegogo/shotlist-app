import streamlit as st
import requests
import json
import os
import urllib.parse
import random

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演助手 (自動偵測版)", layout="wide", page_icon="🎬")

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
    v_type = st.selectbox("類型", ["Vlog", "短影音", "廣告", "微電影"])
    v_topic = st.text_input("主題", "台北 101 跨年煙火")
    v_dur = st.slider("長度", 1, 10, 3)
    v_desc = st.text_area("描述", "熱鬧、感動")
    btn = st.button("🚀 生成分鏡 + 圖片", type="primary")

# --- 🧠 核心：自動尋找可用的模型 ---
def get_best_model_url(key):
    # 1. 先嘗試列出所有模型
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        resp = requests.get(list_url)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            # 找出所有支援 generateContent 的模型
            valid_names = [
                m['name'].replace('models/', '') 
                for m in models 
                if 'generateContent' in m.get('supportedGenerationMethods', [])
            ]
            
            # 優先順序：越新的越好
            priority_list = [
                'gemini-2.0-flash', 
                'gemini-1.5-pro', 
                'gemini-1.5-flash', 
                'gemini-1.0-pro',
                'gemini-pro'
            ]
            
            # 挑選一個命中的
            for p in priority_list:
                if p in valid_names:
                    return f"https://generativelanguage.googleapis.com/v1beta/models/{p}:generateContent?key={key}", p
            
            # 如果優先名單都沒有，就隨便拿第一個能用的
            if valid_names:
                return f"https://generativelanguage.googleapis.com/v1beta/models/{valid_names[0]}:generateContent?key={key}", valid_names[0]
                
    except:
        pass
    
    # 2. 如果上面都失敗，回退到最保險的 gemini-pro
    return f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}", "gemini-pro (Fallback)"

def generate_content(key, topic, style, duration, desc):
    # 🔥 自動取得網址
    url, model_name = get_best_model_url(key)
    st.toast(f"正在使用模型：{model_name}") # 顯示在右下角通知
    
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    你是專業導演。請製作 Shot List：
    主題：{topic}, 風格：{style}, 長度：{duration}分, 描述：{desc}
    
    請回傳純 JSON 陣列。每個物件包含：
    {{
        "id": "1",
        "shot_size": "景別 (特寫/中景/全景)",
        "angle": "運鏡",
        "duration": "秒數",
        "visual_keywords": "3-5 個英文單字用於生圖 (例如: night, fireworks, crowd)",
        "description": "繁體中文詳細指導",
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
            st.error(f"模型 {model_name} 回傳錯誤 {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"程式錯誤: {e}")
        return None

if btn:
    with st.spinner("🔍 AI 正在自動切換線路並構思畫面..."):
        shots = generate_content(api_key, v_topic, v_type, v_dur, v_desc)
        
        if shots:
            st.divider()
            for shot in shots:
                c1, c2 = st.columns([1, 1.5])
                
                with c1:
                    try:
                        # 圖片處理
                        keywords = shot.get('visual_keywords', 'scene')
                        safe_kw = urllib.parse.quote(keywords)
                        seed = random.randint(0, 999)
                        img_url = f"https://image.pollinations.ai/prompt/{safe_kw}?width=800&height=450&nologo=true&model=flux&seed={seed}"
                        st.image(img_url, use_container_width=True)
                    except:
                        st.warning("圖片載入失敗")
                
                with c2:
                    st.markdown(f"### 🎬 鏡頭 {shot['id']}")
                    # 標籤
                    st.markdown(f"""
                    <span style="background-color:#eee; padding:4px; border-radius:4px;">📏 {shot.get('shot_size','')}</span>
                    <span style="background-color:#eee; padding:4px; border-radius:4px;">🔄 {shot.get('angle','')}</span>
                    <span style="background-color:#eee; padding:4px; border-radius:4px;">⏱️ {shot.get('duration','')}</span>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.info(f"**🎥 指導：** {shot.get('description','')}")
                    st.caption(f"🔊 {shot.get('audio','')}")
                    
                    st.file_uploader(f"📹 拍攝 ({shot['id']})", type=['mp4', 'mov'], key=shot['id'])
                
                st.divider()
        else:
            st.error("生成失敗。")
