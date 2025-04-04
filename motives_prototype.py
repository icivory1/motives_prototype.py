# motives_prototype.py

import streamlit as st
import random

# === Mock Interview Data ===
mock_transcript = [
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
    6: "🎯 This could sound like a pitch — stay curious about *their* process."
}

# === Streamlit UI ===
st.set_page_config(page_title="Motives by AbleAI", layout="wide")
st.title("🎙️ Motives by AbleAI")
st.caption("User Research Interview Assistant — Coaching Mode Enabled")

col1, col2 = st.columns([3, 1])

with col1:
    focus_mode = st.toggle("🧘 Focus Mode", value=False)

    st.markdown("---")
    st.subheader("📝 Transcript")
    for i, (speaker, line) in enumerate(mock_transcript):
        is_question = speaker == "You"
        line_display = f"**{speaker}:** {line}"

        if not focus_mode and is_question and i in coaching_tips:
            st.markdown(f"{line_display}  ")
            st.markdown(f"<span style='color:gray;font-size:0.9em'>{coaching_tips[i]}</span>", unsafe_allow_html=True)
        else:
            st.markdown(line_display)

with col2:
    if not focus_mode:
        st.subheader("🧠 Coaching Summary")
        st.success("You stayed focused on their past actions.")
        st.info("Try slowing down when asking rapid-fire questions.")
        st.warning("Avoid pitching — keep exploring their world.")

    st.markdown("---")
    st.markdown("**💾 This is a mock prototype of a real-time interview assistant.**")
    st.markdown("**Coming soon:** live transcription, question suggestions, Notion export.")
