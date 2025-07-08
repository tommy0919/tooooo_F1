# f1_qa_app.py  ── 2025-07-08 完全版
import os, requests, feedparser, streamlit as st, openai

# ───────────────────────────────
# 1. OpenAI クライアント
api_key = st.secrets["OPENAI_API_KEY"]    # Streamlit Cloud の Secrets で設定済み
client = openai.OpenAI(api_key=api_key)

# ───────────────────────────────
# 2. データ取得関数

def get_driver_list(season="2025"):
    """Ergast API でシーズンのドライバー一覧を取得"""
    url = f"http://ergast.com/api/f1/{season}/drivers.json"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        drivers = res.json()["MRData"]["DriverTable"]["Drivers"]
        return "\n".join(
            f"・{d['givenName']} {d['familyName']}（{d['nationality']}）"
            for d in drivers
        ) or "データなし"
    except Exception as e:
        return f"取得エラー: {e}"

def get_latest_race_result():
    """今季最後に終了したレース結果を取得（順位＋ドライバー＋チーム）"""
    url = "http://ergast.com/api/f1/current/last/results.json"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        race = res.json()["MRData"]["RaceTable"]["Races"][0]
        header = f"{race['raceName']}（{race['Circuit']['circuitName']}）結果"
        results = "\n".join(
            f"{r['position']}. {r['Driver']['familyName']}（{r['Constructor']['name']}）"
            for r in race["Results"][:10]  # 上位10台
        )
        return f"{header}\n{results}"
    except Exception as e:
        return f"レース結果取得エラー: {e}"

def get_latest_news_titles(max_items=3):
    """motorsport.com RSS から最新ニュース見出しを取得"""
    try:
        feed = feedparser.parse("https://www.motorsport.com/rss/f1/news/")
        return "\n".join(f"・{e.title}" for e in feed.entries[:max_items]) or "ニュースなし"
    except Exception as e:
        return f"ニュース取得エラー: {e}"

# ───────────────────────────────
# 3. Streamlit UI

st.title("🏎️ F1 なんでも質問AI・2025最新版")
st.caption("ドライバー・レース結果・最新ニュースを自動参照して回答します。")

question = st.text_input("🔍 質問を入力してください", placeholder="例：2025年メルセデスのドライバーは？")

if question:
    with st.spinner("GPT が回答を生成中…"):
        # 最新データを取得
        drivers_text = get_driver_list()
        race_text    = get_latest_race_result()
        news_text    = get_latest_news_titles()

        # GPT へのプロンプト
        prompt = f"""
あなたは F1 の専門家で、最新情報にも精通しています。
以下の最新データを参考に、ユーザーの質問に日本語で詳しく答えてください。

【2025年ドライバー一覧】
{drivers_text}

【直近レース結果】
{race_text}

【最近の主要ニュース】
{news_text}

質問: {question}
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        st.markdown("### 🧠 回答")
        st.write(response.choices[0].message.content.strip())
