# f1_news_app.py

import openai
import feedparser
import streamlit as st
import textwrap
import os

# 🔐 OpenAI APIキーを取得（環境変数 or 入力フォーム）
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# 🌐 F1 ニュースフィード（Motorsport.com）
RSS_URL = "https://www.motorsport.com/rss/f1/news/"
feed = feedparser.parse(RSS_URL)
articles = feed.entries[:3]

# GPT 要約関数（v1系対応）
def summarize_article(title, link):
    client = openai.OpenAI(api_key=api_key)
    prompt = textwrap.dedent(f"""
    あなたはF1の専門家です。以下のニュースを日本語で簡潔に要約してください。
    レース結果、ドライバーの発言、ファッション、来場セレブなども含めてください。

    タイトル: {title}
    URL: {link}
    """)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# 🔽 Streamlit画面の表示部分
st.title("🏁 F1 ニュース速報 × GPT 要約")
st.write("最新のF1ニュースをAIが日本語でわかりやすく要約します。")

if not api_key:
    st.warning("OpenAI APIキーを入力してください")
else:
    for entry in articles:
        with st.expander(entry.title):
            st.markdown(f"[元記事リンクはこちら]({entry.link})")
            with st.spinner("GPTが要約中..."):
                summary = summarize_article(entry.title, entry.link)
                st.markdown(summary)