import streamlit as st
import requests
import json

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演助手", layout="wide", page_icon="🎬")
st.title("🎬 AI 影片分鏡助手")
st.markdown("輸入影片構想，AI 幫您規劃詳細的分鏡鏡頭。")

# --- 嘗試自動讀取 Key ---
try:
    # 從 Streamlit Secrets (保險箱) 讀取 Key
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    # 如果是在本機跑，或者沒設定 Secrets，就讓使用者輸入 (備用方案)
    with st.sidebar:
        api_key = st.text_input("請輸入 Google API Key", type="password")

# --- 側邊欄：輸入設定 ---
with st.sidebar:
    st.header("📝 影片設定")
    v_type = st.selectbox("影片類型", ["Vlog", "短影音", "廣告", "微電影"])
    v_topic = st.text_input("主題", "台北 101 跨年煙火")
    v_dur = st.slider("長度 (分鐘)", 1, 10, 3)
    v_desc = st.text_area("描述", "熱鬧、感動")
    
    btn = st.button("🚀 生成分鏡表", type="primary")

# --- 核心功能 ---
def generate_shot_list(key, video_type, topic, duration, description):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    prompt_text = f"""
    你是專業導演。請製作 Shot List：
    類型：{video_type}, 主題：{topic}, 長度：{duration}分, 描述：{description}
    請用 Markdown 表格輸出：鏡頭編號, 景別, 運鏡, 秒數, 畫面, 備註。用繁體中文。
    """
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- 執行 ---
if btn:
    if not api_key:
        st.error("⚠️ 找不到 API Key！請在 Secrets 設定或側邊欄輸入。")
    else:
        with st.spinner("⚡ AI 導演正在構思中..."):
            st.markdown(generate_shot_list(api_key, v_type, v_topic, v_dur, v_desc))
