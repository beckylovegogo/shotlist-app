import streamlit as st
import requests
import json
import os
import urllib.parse

# --- 頁面設定 ---
st.set_page_config(page_title="AI 導演 + 視覺分鏡", layout="wide", page_icon="🎬")
st.title("🎬 AI 導演：視覺分鏡助手")

# 自動讀取 API Key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

# --- 側邊欄 ---
with st.sidebar:
    if not api_key:
        api_key = st.text_input("輸入 Google API Key", type="password")
    else:
        st.success("✅ 已連線")
        
    v_type = st.selectbox("類型", ["Vlog", "短影音", "廣告", "微電影"])
    v_topic = st.text_input("主題", "台北 101 跨年煙火")
    v_dur = st.slider("長度", 1, 10, 3)
    v_desc = st.text_area("描述", "熱鬧、感動")
    btn = st.button("🚀 生成視覺分鏡表", type="primary")

# --- 核心功能：生成文字腳本 ---
def generate_shot_list_json(key, video_type, topic, duration, description):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    
    # 關鍵修改：要求 AI 回傳 JSON 格式，方便我們程式讀取並拿去生圖
    prompt = f"""
    你是專業導演。請製作 Shot List：
    類型：{video_type}, 主題：{topic}, 長度：{duration}分, 描述：{description}
    
    請回傳一個純 JSON 陣列 (Array)，不要有任何 Markdown 標記。
    每個物件包含：
    - "id": 鏡頭編號
    - "visual": 畫面內容描述 (這段描述將用來生成 AI 圖片，請描述得具體且充滿畫面感，英文尤佳)
    - "action": 運鏡與動作指導
    - "audio": 聲音備註
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text']
            # 清理可能的多餘標記
            text = text.replace("```json", "").replace("```", "")
            return json.loads(text)
        else:
            return None
    except Exception as e:
        return None

# --- 顯示介面 ---
if btn and api_key:
    with st.spinner("🤖 導演正在寫腳本 + 繪師正在畫圖..."):
        shots = generate_shot_list_json(api_key, v_type, v_topic, v_dur, v_desc)
        
        if shots:
            st.divider()
            # 使用卡片式佈局來呈現每一個鏡頭
            for shot in shots:
                # 建立兩欄：左邊是圖片，右邊是指導
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    # ✨ 魔法：用描述直接生成圖片
                    prompt_safe = urllib.parse.quote(shot['visual'])
                    image_url = f"https://image.pollinations.ai/prompt/{prompt_safe}?width=800&height=450&nologo=true"
                    st.image(image_url, caption="AI 概念圖", use_container_width=True)
                
                with c2:
                    st.subheader(f"鏡頭 {shot['id']}")
                    st.markdown(f"**🎥 畫面：** {shot['visual']}")
                    st.markdown(f"**🎬 指導：** {shot['action']}")
                    st.markdown(f"**🔊 聲音：** {shot['audio']}")
                    
                    # 🔴 喚醒相機功能
                    # 在手機上點這個，會跳出選項問你要「錄影」還是「選檔」
                    st.file_uploader(f"上傳/拍攝鏡頭 {shot['id']}", type=['mp4', 'mov'], key=shot['id'])
                
                st.divider()
        else:
            st.error("生成失敗，請重試")
