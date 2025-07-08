import os, requests, feedparser, fitz, streamlit as st, openai

# ━━━ OpenAI setup ━━━
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ━━━ Session state init ━━━
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ━━━ PDF Reader ━━━
def read_all_pdfs(folder="data"):
    texts = []
    if not os.path.exists(folder):
        return "(PDFデータがありません)"
    for f in os.listdir(folder):
        if f.endswith(".pdf"):
            try:
                with fitz.open(os.path.join(folder, f)) as doc:
                    body = "\n".join(p.get_text() for p in doc)
                    texts.append(f"[{f}]\n{body}")
            except Exception as e:
                texts.append(f"[{f}] 読み込み失敗: {e}")
    return "\n\n".join(texts) or "(PDF情報なし)"

# ━━━ External APIs ━━━
def driver_list_ergast():
    try:
        res = requests.get("http://ergast.com/api/f1/2025/drivers.json", timeout=5)
        drivers = res.json()["MRData"]["DriverTable"]["Drivers"]
        if not drivers:
            return "Ergastにはドライバーがなし"
        return "\n".join(f"・{d['givenName']} {d['familyName']}" for d in drivers)
    except Exception as e:
        return f"エラー: {e}"

def last_race_result():
    try:
        res = requests.get("http://ergast.com/api/f1/current/last/results.json", timeout=5)
        race = res.json()["MRData"]["RaceTable"]["Races"][0]
        rows = "\n".join(
            f"{r['position']}. {r['Driver']['familyName']} ({r['Constructor']['name']})"
            for r in race["Results"][:10]
        )
        return f"{race['raceName']} \u7d50\u679c\n{rows}"
    except Exception as e:
        return f"エラー: {e}"

def latest_news(max_items=3):
    try:
        feed = feedparser.parse("https://www.motorsport.com/rss/f1/news/")
        return "\n".join(f"・{e.title}" for e in feed.entries[:max_items])
    except Exception as e:
        return f"エラー: {e}"

# ━━━ UI ━━━
st.title("🏎️ F1チャットAI 2025")
st.caption("最新PDFやレース結果、ニュースを参照して回答します")

# user input
user_input = st.text_input("質問を入力", key="input")
if user_input:
    # show immediately in chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # gather knowledge
    pdf_text = read_all_pdfs()
    drivers = driver_list_ergast()
    race_text = last_race_result()
    news_text = latest_news()

    prompt = f"""
F1の専門家として、以下の情報を参照しながら、ユーザーの質問に日本語で簡潔に回答してください。

[PDF]
{pdf_text}

[2025ドライバー]
{drivers}

[最新レース]
{race_text}

[最新ニュース]
{news_text}

質問: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"回答失敗: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()  # refresh to clear input and show chat

# display chat history (LINE風)
for msg in reversed(st.session_state.chat_history):
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; color:white; background-color:#0f62fe; padding:8px 12px; border-radius:12px; margin:4px 0;'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; color:black; background-color:#f4f4f4; padding:8px 12px; border-radius:12px; margin:4px 0;'>{msg['content']}</div>", unsafe_allow_html=True)
