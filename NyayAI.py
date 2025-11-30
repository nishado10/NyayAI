"""
NyayAI - Gen-Z Modern UI (Notion/Linear style)
OCR via OCR.Space API (Streamlit-cloud compatible)
TTS via gTTS
"""

import streamlit as st
from PIL import Image
import requests
import base64
import io
from gtts import gTTS
import tempfile
import os
import textwrap

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="NyayAI — Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

OCR_SPACE_API_KEY = "K89465762388957"   # ← paste your key here


# ----------------------------------------------------
# GEN-Z CLEAN CSS
# ----------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
    color: #0f172a;
}

.main > .block-container {
    padding-top: 34px;
    padding-left: 70px;
    padding-right: 70px;
    max-width: 1150px;
}

.hero {
    background: #ffffff;
    padding: 28px;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    margin-bottom: 30px;
}

.card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 18px rgba(16,24,40,0.04);
    border: 1px solid #e2e8f0;
    margin-bottom: 20px;
}

.pill {
    display:inline-block;
    background: linear-gradient(90deg,#6366f1,#7c3aed);
    color:white;
    font-weight:600;
    padding:6px 14px;
    border-radius:999px;
    font-size:13px;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 10px;
}

textarea, .stTextArea textarea {
    background:#fbfdff!important;
    border-radius:10px!important;
    border:1px solid #e6eef9!important;
    padding:12px!important;
    color:#0f172a!important;
}

.stButton > button {
    background: linear-gradient(90deg,#6366f1,#7c3aed);
    color:white;
    border-radius:10px;
    padding:10px 18px;
    border:none;
    font-weight:600;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(99,102,241,0.12);
}

footer { visibility:hidden; }

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# OCR via OCR.Space
# ----------------------------------------------------
def ocr_space_image(image_bytes, language="eng,mar"):
    url = "https://api.ocr.space/parse/image"
    files = {"file": image_bytes}
    data = {
        "apikey": OCR_SPACE_API_KEY,
        "language": language,
        "OCREngine": 2,
        "scale": True,
        "isTable": False
    }
    response = requests.post(url, data=data, files=files)
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return {"error": result.get("ErrorMessage", "OCR error"), "text": ""}

    text = result["ParsedResults"][0]["ParsedText"]
    return {"error": None, "text": text.strip()}


# ----------------------------------------------------
# MOCK LLM
# ----------------------------------------------------
def mock_llm(text):
    t = (text or "").lower()
    if any(k in t for k in ["evict", "notice", "नोटीस"]):
        return {
            "summary": "Eviction-related document detected.",
            "risk": "Medium",
            "draft": """To,
The Landlord,
Subject: Reply to eviction notice

Dear Sir/Madam,
I received your eviction notice dated [DATE]. Kindly clarify the grounds and provide supporting documents.
Regards,
[Your name]"""
        }
    if any(k in t for k in ["deposit", "refund", "डिपॉझिट"]):
        return {
            "summary": "Deposit refund issue detected.",
            "risk": "Low",
            "draft": """To,
The Landlord,
Subject: Request for refund of security deposit

Dear Sir/Madam,
The security deposit is refundable as per the agreement. I request prompt processing.
Regards,
[Your name]"""
        }
    return {
        "summary": "General legal document detected.",
        "risk": "Low",
        "draft": """To,
Concerned,
Subject: Request for clarification

Dear Sir/Madam,
Please share the necessary details and timelines so I can proceed.
Regards,
[Your name]"""
    }


# ----------------------------------------------------
# TTS
# ----------------------------------------------------
def tts_bytes(text, lang="mr"):
    try:
        tts = gTTS(text=text, lang=lang)
    except:
        tts = gTTS(text=text, lang="en")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    audio = open(tmp.name, "rb").read()
    os.unlink(tmp.name)
    return audio


# ----------------------------------------------------
# UI: HERO
# ----------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="pill">NyayAI</div>
    <h2 style="margin-top:15px;margin-bottom:4px;color:#0b1220;font-weight:700;">AI Legal Assistant</h2>
    <div style="color:#475569;font-size:15px;">Gen-Z clean design · Marathi + English · OCR + TTS · Prototype only</div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# LAYOUT: TWO COLUMNS
# ----------------------------------------------------
col1, col2 = st.columns([1.1, 0.9], gap="large")


# ----------------------------------------------------
# LEFT COLUMN — DOCUMENT OCR
# ----------------------------------------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Upload Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload photo/scan (JPG/PNG)", type=["png", "jpg", "jpeg"])

    if uploaded:
        img_bytes = uploaded.read()
        st.image(img_bytes, caption="Preview", use_column_width=True)

        if st.button("Run OCR & Analyze"):
            with st.spinner("Extracting text..."):
                res = ocr_space_image(img_bytes)

            if res["error"]:
                st.error(res["error"])
            else:
                extracted = res["text"]
                st.text_area("OCR Output", extracted, height=220)

                llm = mock_llm(extracted)

                st.markdown("### AI Summary")
                st.write(llm["summary"])
                st.write("**Risk Level:**", llm["risk"])

                st.markdown("### Generated Draft")
                st.text_area("Draft", llm["draft"], height=200)

                if st.button("Play TTS"):
                    lang = "mr" if any(ch in extracted for ch in "अआइईउऊएऐओऔकखगघ") else "en"
                    st.audio(tts_bytes(llm["draft"], lang), format="audio/mp3")

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# RIGHT COLUMN — AUDIO + TEMPLATES
# ----------------------------------------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎤 Voice Input (Mock STT)</div>', unsafe_allow_html=True)

    audio_file = st.file_uploader("Upload audio file", type=["mp3", "wav", "webm", "m4a"])

    if audio_file:
        st.audio(audio_file)

        if st.button("Transcribe (Mock)"):
            transcript = "मला माझ्या भाडेकराराबाबत माहिती हवी आहे"
            st.text_area("Transcript", transcript)

            llm = mock_llm(transcript)
            st.text_area("Draft (from audio)", llm["draft"], height=180)

            if st.button("Play Audio Draft"):
                st.audio(tts_bytes(llm["draft"], "mr"))

    # Templates
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Quick Templates</div>', unsafe_allow_html=True)

    option = st.selectbox("Choose template", ["Select...", "Eviction Reply", "Deposit Refund Request", "General"])

    if st.button("Generate Template"):
        if option == "Eviction Reply":
            draft = mock_llm("eviction")["draft"]
        elif option == "Deposit Refund Request":
            draft = mock_llm("deposit")["draft"]
        elif option == "General":
            draft = mock_llm("general")["draft"]
        else:
            draft = ""

        if draft:
            st.text_area("Template Output", draft, height=200)

            if st.button("Play Template TTS"):
                st.audio(tts_bytes(draft, "mr"))

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
st.markdown("""
<div class="card" style="text-align:center;margin-top:20px;">
    <div style="color:#64748b;font-size:14px;">
        NyayAI · Prototype · Not a substitute for legal advice
    </div>
</div>
""", unsafe_allow_html=True)
