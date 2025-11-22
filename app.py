{\rtf1\ansi\ansicpg950\cocoartf2580
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;\f1\fnil\fcharset136 STSongti-TC-Regular;\f2\fnil\fcharset0 AppleColorEmoji;
}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww14340\viewh10340\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf2 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import streamlit as st import requests import json # --- 
\f1 \'ad\'b6\'ad\'b1\'b3\'5d\'a9\'77
\f0  --- st.set_page_config(page_title="AI 
\f1 \'be\'c9\'ba\'74\'a7\'55\'a4\'e2
\f0 ", layout="wide", page_icon="
\f2 \uc0\u55356 \u57260 
\f0 ") st.title("
\f2 \uc0\u55356 \u57260 
\f0  AI 
\f1 \'bc\'76\'a4\'f9\'a4\'c0\'c3\'e8\'a7\'55\'a4\'e2
\f0 ") st.markdown("
\f1 \'bf\'e9\'a4\'4a\'bc\'76\'a4\'f9\'ba\'63\'b7\'51\'a1\'41
\f0 AI 
\f1 \'c0\'b0\'b1\'7a\'b3\'57\'b9\'ba\'b8\'d4\'b2\'d3\'aa\'ba\'a4\'c0\'c3\'e8\'c3\'e8\'c0\'59\'a1\'43
\f0 ") # --- 
\f1 \'b0\'bc\'c3\'e4\'c4\'e6\'a1\'47\'b3\'5d\'a9\'77\'bb\'50\'bf\'e9\'a4\'4a
\f0  --- with st.sidebar: st.header("
\f2 \uc0\u55357 \u56593 
\f0  
\f1 \'b3\'5d\'a9\'77
\f0 ") # 
\f1 \'c5\'fd\'a8\'cf\'a5\'ce\'aa\'cc\'a6\'db\'a4\'76\'bf\'e9\'a4\'4a
\f0  Key
\f1 \'a1\'41\'b3\'6f\'bc\'cb\'b3\'cc\'a6\'77\'a5\'fe
\f0  api_key = st.text_input("
\f1 \'bd\'d0\'bf\'e9\'a4\'4a
\f0  Google Gemini API Key", type="password") st.caption("
\f1 \'a8\'53\'a6\'b3
\f0  Key? [
\f1 \'c2\'49\'a6\'b9\'a7\'4b\'b6\'4f\'a8\'fa\'b1\'6f
\f0 ](https://aistudio.google.com/app/apikey)") st.divider() st.header("
\f2 \uc0\u55357 \u56541 
\f0  
\f1 \'bc\'76\'a4\'f9\'b3\'5d\'a9\'77
\f0 ") v_type = st.selectbox("
\f1 \'bc\'76\'a4\'f9\'c3\'fe\'ab\'ac
\f0 ", ["Vlog (
\f1 \'a5\'cd\'ac\'a1\'ac\'f6\'bf\'fd
\f0 )", "Reels/TikTok 
\f1 \'b5\'75\'bc\'76\'ad\'b5
\f0 ", "
\f1 \'b0\'d3\'b7\'7e\'bc\'73\'a7\'69
\f0 ", "
\f1 \'b7\'4c\'b9\'71\'bc\'76
\f0 ", "YouTube 
\f1 \'aa\'f8\'a4\'f9
\f0 "]) v_topic = st.text_input("
\f1 \'a5\'44\'c3\'44
\f0 ", "
\f1 \'a5\'78\'a5\'5f
\f0  101 
\f1 \'b8\'f3\'a6\'7e\'b7\'cf\'a4\'f5
\f0 ") v_dur = st.slider("
\f1 \'aa\'f8\'ab\'d7
\f0  (
\f1 \'a4\'c0\'c4\'c1
\f0 )", 1, 10, 3) v_desc = st.text_area("
\f1 \'a4\'ba\'ae\'65\'b4\'79\'ad\'7a
\f0 ", "
\f1 \'bc\'f6\'be\'78\'a1\'42\'b7\'50\'b0\'ca\'a1\'42\'b1\'6a\'bd\'d5\'b7\'cf\'a4\'f5\'aa\'ba\'a7\'a7\'c6\'5b
\f0 ") btn = st.button("
\f2 \uc0\u55357 \u56960 
\f0  
\f1 \'a5\'cd\'a6\'a8\'a4\'c0\'c3\'e8\'aa\'ed
\f0 ", type="primary") # --- 
\f1 \'ae\'d6\'a4\'df\'a5\'5c\'af\'e0\'a8\'e7\'bc\'c6
\f0  --- def generate_shot_list(api_key, video_type, topic, duration, description): # 
\f1 \'a8\'cf\'a5\'ce
\f0  Gemini 2.0 Flash (
\f1 \'a5\'d8\'ab\'65\'b3\'cc\'b7\'73\'a5\'42\'a4\'e4\'b4\'a9\'ab\'d7\'b0\'aa\'aa\'ba\'bc\'d2\'ab\'ac
\f0 ) url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=\{api_key\}" headers = \{'Content-Type': 'application/json'\} prompt_text = f""" 
\f1 \'a7\'41\'ac\'4f\'a5\'d1
\f0  Google Gemini 2.0 
\f1 \'c5\'58\'b0\'ca\'aa\'ba\'b1\'4d\'b7\'7e\'be\'c9\'ba\'74\'a1\'43\'bd\'d0\'bb\'73\'a7\'40\'a4\'40\'a5\'f7
\f0  Shot List
\f1 \'a1\'47
\f0  
\f1 \'bc\'76\'a4\'f9\'c3\'fe\'ab\'ac\'a1\'47
\f0 \{video_type\} 
\f1 \'a5\'44\'c3\'44\'a1\'47
\f0 \{topic\} 
\f1 \'aa\'f8\'ab\'d7\'a1\'47
\f0 \{duration\} 
\f1 \'a4\'c0\'c4\'c1
\f0  
\f1 \'b4\'79\'ad\'7a\'a1\'47
\f0 \{description\} 
\f1 \'bd\'d0\'a5\'ce
\f0  Markdown 
\f1 \'aa\'ed\'ae\'e6\'bf\'e9\'a5\'58\'a1\'41\'aa\'ed\'ae\'e6\'c4\'e6\'a6\'ec\'a5\'5d\'a7\'74\'a1\'47
\f0  - 
\f1 \'c3\'e8\'c0\'59\'bd\'73\'b8\'b9
\f0  (Shot ID) - 
\f1 \'b4\'ba\'a7\'4f
\f0  (Shot Size) - 
\f1 \'b9\'42\'c3\'e8
\f0  (Movement) - 
\f1 \'b9\'77\'a6\'f4\'ac\'ed\'bc\'c6
\f0  (Duration) - 
\f1 \'b5\'65\'ad\'b1\'a4\'ba\'ae\'65
\f0  (Visual) - 
\f1 \'c1\'6e\'ad\'b5
\f0 /
\f1 \'b3\'c6\'b5\'f9
\f0  (Audio/Notes) 
\f1 \'bd\'d0\'a5\'ce\'c1\'63\'c5\'e9\'a4\'a4\'a4\'e5\'a6\'5e\'b5\'aa\'a1\'43
\f0  """ data = \{"contents": [\{"parts": [\{"text": prompt_text\}]\}]\} try: response = requests.post(url, headers=headers, json=data) if response.status_code == 200: return response.json()['candidates'][0]['content']['parts'][0]['text'] else: return f"
\f2 \uc0\u10060 
\f0  
\f1 \'b3\'73\'bd\'75\'bf\'f9\'bb\'7e
\f0  (Code \{response.status_code\}):\\n\{response.text\}" except Exception as e: return f"
\f2 \uc0\u10060 
\f0  
\f1 \'b5\'7b\'a6\'a1\'bf\'f9\'bb\'7e\'a1\'47
\f0 \{str(e)\}" # --- 
\f1 \'b0\'f5\'a6\'e6\'c5\'de\'bf\'e8
\f0  --- if btn: if not api_key: st.error("
\f2 \uc0\u9888 \u65039 
\f0  
\f1 \'bd\'d0\'a5\'fd\'a6\'62\'a5\'aa\'b0\'bc\'c4\'e6\'a6\'ec\'bf\'e9\'a4\'4a\'b1\'7a\'aa\'ba
\f0  API Key 
\f1 \'b3\'e1\'a1\'49
\f0 ") else: with st.spinner("
\f2 \uc0\u9889 
\f0  AI 
\f1 \'be\'c9\'ba\'74\'a5\'bf\'a6\'62\'ba\'63\'ab\'e4\'a4\'c0\'c3\'e8
\f0 ..."): result = generate_shot_list(api_key, v_type, v_topic, v_dur, v_desc) st.markdown("### 
\f2 \uc0\u55357 \u56523 
\f0  
\f1 \'b1\'7a\'aa\'ba\'a9\'e7\'c4\'e1\'a4\'c0\'c3\'e8\'aa\'ed
\f0 ") st.markdown(result)}