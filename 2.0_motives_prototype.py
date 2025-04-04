# motives_prototype.py

import streamlit as st
import random
import time
import openai
import sounddevice as sd
import queue
import whisper
import numpy as np
import threading
import webbrowser
from notion_client import Client as NotionClient

# === Config ===
openai.api_key = st.secrets["openai_api_key"]
notion = NotionClient(auth=st.secrets["notion_token"])
notion_db_id = st.secrets["notion_db_id"]
model = whisper.load_model("base")

audio_q = queue.Queue()
def audio_callback(indata, frames, time, status):
    audio_q.put(indata.copy())

def transcribe_stream():
    buffer = np.zeros((0, 1), dtype=np.float32)
    while True:
        chunk = audio_q.get()
        buffer = np.concatenate((buffer, chunk))
        if buffer.shape[0] > 16000 * 5:  # 5 seconds
            audio_segment = buffer[-16000 * 5:]
            audio_path = "temp.wav"
            whisper.audio.write_audio(audio_path, audio_segment, 16000)
            result = model.transcribe(audio_path)
            st.session_state.transcript.append(("Customer", result['text'].strip()))
            buffer = buffer[-16000:]  # Keep last second

# === Mock Interview Data ===
if "transcript" not in st.session_state:
    st.session_state.transcript = [
        ("You", "Can you walk me through how you currently manage your supplier relationships?"),
        ("Customer", "Yeah, we mostly rely on spreadsheets and email. Each project manager kind of has their own system, which can get messy."),
        ("You", "Can you tell me about the last time something went wrong because of that system?"),
        ("Customer", "Just last week, one of our PMs accidentally double-booked a supplier for two sites on the same day. We lost half a day on both sites just figuring it out."),
        ("You", "Wow. That sounds frustrating. What did you do to fix it?"),
        ("Customer", "We just added another column in the spreadsheet and told everyone to triple-check before confirming anything."),
        ("You", "Have you looked into any software tools to solve that?"),
        ("Customer", "We tried Procore and CoConstruct, but they felt bloated. Too many features we didn’t need."),
        ("You", "What would your dream solution look like?"),
        ("Customer", "A shared calendar with conflict alerts and basic contact tracking. No fluff."),
    ]

coaching_tips = {
    1: "✅ Great use of 'Talk me through the last time that happened.'",
    3: "⚠️ Consider pausing longer here — let them reflect.",
    6: "🎯 This could sound like a pitch — stay curious about *their* process.",
    8: "💡 Ask why that feature matters to them — get to the emotion behind the request."
}

suggested_questions = [
    "What are the implications of that happening again?",
    "How much time or money does this cost you each month?",
    "Why do you bother using spreadsheets instead of something else?",
    "What would make you switch tools?",
    "Who else should I talk to about this problem?"
]

# === Streamlit UI ===
st.set_page_config(page_title="Motives by AbleAI", layout="wide")
st.title("🎙️ Motives by AbleAI")
st.caption("User Research Interview Assistant — Coaching Mode Enabled")

col1, col2 = st.columns([3, 1])

with col1:
    focus_mode = st.toggle("🧘 Focus Mode", value=False)
    empathy_mode = st.toggle("💓 Empathy Nudges", value=True)
    coaching_mode = st.toggle("🧠 Coaching Mode", value=True)
    transcript_buffer = []

    # Audio device selector
    st.markdown("---")
    st.subheader("🎚️ Audio Input Device")
    devices = sd.query_devices()
    input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]
    selected_device = st.selectbox("Choose audio input device:", input_devices)

    st.markdown("---")
    st.subheader("📝 Transcript")
    for i, (speaker, line) in enumerate(st.session_state.transcript):
        is_question = speaker == "You"
        line_display = f"**{speaker}:** {line}"

        if not focus_mode and is_question and coaching_mode and i in coaching_tips:
            st.markdown(f"{line_display}  ")
            st.markdown(f"<span style='color:gray;font-size:0.9em'>{coaching_tips[i]}</span>", unsafe_allow_html=True)
        elif empathy_mode and speaker == "Customer" and any(word in line.lower() for word in ["frustrating", "annoying", "overwhelming"]):
            st.markdown(line_display)
            st.markdown("<span style='color:purple;font-size:0.9em'>🫂 Empathy prompt: Reflect their emotions to build rapport.</span>", unsafe_allow_html=True)
        else:
            st.markdown(line_display)

        transcript_buffer.append({"speaker": speaker, "text": line})

    if st.button("📤 Export Transcript to Notion"):
        for entry in transcript_buffer:
            notion.pages.create(
                parent={"database_id": notion_db_id},
                properties={
                    "Speaker": {"title": [{"text": {"content": entry["speaker"]}}]},
                    "Text": {"rich_text": [{"text": {"content": entry["text"]}}]}
                }
            )
        st.success("Transcript exported to Notion.")

    st.markdown("---")
    st.subheader("💬 Suggested Follow-up Questions")
    customer_lines = [line for speaker, line in st.session_state.transcript if speaker == "Customer"]
    last_customer_line = customer_lines[-1] if customer_lines else ""

    dynamic_suggestions = [
        q for q in suggested_questions if any(word in last_customer_line.lower() for word in ["cost", "time", "spreadsheet", "problem", "again"])
    ]

    for q in random.sample(dynamic_suggestions or suggested_questions, 2):
        st.markdown(f"🔹 {q}")

    if st.button("🎙️ Start Real-time Transcription"):
        threading.Thread(target=transcribe_stream, daemon=True).start()
        sd.InputStream(callback=audio_callback, channels=1, samplerate=16000, device=selected_device).start()
        st.success(f"Transcription started using device: {selected_device}")

    st.markdown("---")
    st.subheader("📞 Start a Call")
    if st.button("Start Zoom Call"):
        webbrowser.open("https://zoom.us/start/videomeeting")
    if st.button("Start Google Meet"):
        webbrowser.open("https://meet.google.com/new")

with col2:
    if not focus_mode and coaching_mode:
        st.subheader("🧠 Coaching Summary")
        st.success("You stayed focused on their past actions.")
        st.info("Try slowing down when asking rapid-fire questions.")
        st.warning("Avoid pitching — keep exploring their world.")

    st.markdown("---")
    st.markdown("**💾 Real-time Interview Assistant Features:**")
    st.markdown("- ✅ Whisper transcription enabled")
    st.markdown("- ✅ Zoom + Google Meet integration")
    st.markdown("- ✅ Empathy + Coaching Modes")
    st.markdown("- ✅ Notion DB integration")
    st.markdown("- ✅ Smart follow-up question generation")
    st.markdown("- ✅ Audio device selection for Zoom/Meet sync")
