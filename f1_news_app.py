import streamlit as st
import openai
import os
import glob
from PyPDF2 import PdfReader

# タイトルと説明
st.set_page_config(page_title="F1チャットAI 2025", layout="wide")
st.title("🏎️ F1チャットAI 2025")
st.markdown("最新PDFやレース結果、ニュースを参照して回答します")

# OpenAI APIキーの読み込み
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

# セッションで会話履歴を管理
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📄 PDFからテキストを抽出
def load_pdf_texts(folder_path="./pdfs"):
    texts = []
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            texts.append(text)
    return "\n\n".join(texts)

# 📥 ユーザー入力
user_input = st.text_input("質問を入力", placeholder="例：2025年のF1ドライバーラインナップを教えて")

# 💬 会話ログの表示
for msg in st.session_state.chat_history:
    st.markdown(f"**🧑‍💬 ユーザー：** {msg['user']}")
    st.markdown(f"**🤖 回答：** {msg['bot']}")

# 🔍 回答生成
if user_input:
    context = load_pdf_texts()
    system_prompt = f"""
    あなたはF1の専門家AIです。
    以下のコンテキストに基づいて、ユーザーからの質問に日本語で丁寧に答えてください。
    コンテキストは最新のニュース記事やレース情報などです。
    コンテキスト:
    {context}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]
        )
        answer = response.choices[0].message["content"]

    except Exception as e:
        answer = f"⚠️ エラーが発生しました: {e}"

    # 履歴に追加
    st.session_state.chat_history.append({
        "user": user_input,
        "bot": answer
    })

    # 空欄にして再表示（rerunは不要）
    st.experimental_set_query_params()

    st.experimental_rerun()
