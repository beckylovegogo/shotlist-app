import streamlit as st
import requests
import json

# --- 頁面基礎設定 ---
st.set_page_config(page_title="AI 導演助手", layout="wide", page_icon="🎬")

st.title("🎬 AI 影片分鏡助手")
st.markdown("輸入您的影片構想，AI 幫您規劃詳細的分鏡鏡頭 (Shot List)。")

# --- 側邊欄：設定與輸入 ---
with st.sidebar:
    st.header("🔑 關鍵設定")
    
    # 讓使用者輸入 API Key (密碼模式顯示)
    api_key = st.text_input("請輸入 Google Gemini API Key", type="password")
    st.caption("沒有 Key? [點此免費取得](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    st.header("📝 影片內容設定")
    v_type = st.selectbox("影片類型", ["Vlog (生活紀錄)", "Reels/TikTok 短影音", "商業廣告", "微電影/劇情片", "YouTube 長片"])
    v_topic = st.text_input("主題", "例如：台北 101 跨年煙火")
    v_dur = st.slider("預估長度 (分鐘)", 1, 10, 3)
    v_desc = st.text_area("內容描述", "例如：想要拍出熱鬧、感動的氣氛，強調煙火的壯觀。")
    
    btn = st.button("🚀 開始生成分鏡表", type="primary")

# --- 核心 AI 功能函數 ---
def generate_shot_list(api_key, video_type, topic, duration, description):
    # 使用最新的 Gemini 2.0 Flash 模型
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    你是由 Google Gemini 2.0 驅動的專業導演。請製作一份 Shot List：
    影片類型：{video_type}
    主題：{topic}
    長度：{duration} 分鐘
    描述：{description}
    
    請用 Markdown 表格輸出，表格欄位包含：
    - 鏡頭編號 (Shot ID)
    - 景別 (Shot Size)
    - 運鏡 (Movement)
    - 預估秒數 (Duration)
    - 畫面內容 (Visual)
    - 聲音/備註 (Audio/Notes)
    
    請用繁體中文回答。
    """
    
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        # 發送請求到 Google
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # 成功！解析 JSON 回傳內容
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # 失敗，回傳錯誤訊息
            return f"❌ 連線錯誤 (Code {response.status_code}):\nGoogle 說：{response.text}"
            
    except Exception as e:
        return f"❌ 程式發生錯誤：{str(e)}"

# --- 主程式邏輯 ---
if btn:
    if not api_key:
        st.warning("⚠️ 請先在左側欄位貼上您的 API Key 才能運作喔！")
        st.info("👉 如果您還沒有 Key，請點側邊欄的連結去申請一個。")
    else:
        with st.spinner("⚡ AI 導演正在極速構思分鏡中..."):
            result = generate_shot_list(api_key, v_type, v_topic, v_dur, v_desc)
            
            st.divider()
            st.subheader("📋 您的拍攝分鏡表")
            st.markdown(result)
            st.success("完成！您可以選取表格內容複製到 Excel 或 Notion。")
