import openai
import streamlit as st
import os

# OpenAI APIキーの読み込み（secretsから）
api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# タイトル
st.title("🏎️ F1なんでも質問AI")
st.markdown("F1に関する雑学・サーキット情報・ドライバー・戦略など、なんでも質問してみてください！")

# ユーザー入力
user_input = st.text_input("🔍 質問を入力してください", placeholder="例：シルバーストーンってどんなサーキット？")

# 回答処理
if user_input:
    with st.spinner("GPTが考え中です..."):
        prompt = f"""
あなたはF1の専門家です。以下の質問に対して、日本語で詳しく、初心者にもわかりやすく、正確に解説してください。

質問: {user_input}
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        st.markdown("### 🧠 回答")
        st.write(response.choices[0].message.content.strip())
