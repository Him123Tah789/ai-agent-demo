import streamlit as st
import requests
import time
import uuid

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Explainable AI Agent Demo",
    layout="wide"
)

st.title("🤖 Explainable AI Agent Demo")
st.caption("An AI agent that shows how it thinks and works without human handling")

# -----------------------------
# Per-user Session ID
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -----------------------------
# Layout
# -----------------------------
col1, col2, col3 = st.columns(3)

# -----------------------------
# INPUT PANEL
# -----------------------------
with col1:
    st.header("🟦 Input")

    agent_type = st.selectbox(
        "Select Agent Type",
        [
            "Customer Support",
            "Invoice Processing",
            "Resume Screening"
        ]
    )

    # -----------------------------
    # Document Upload (NEW)
    # -----------------------------
    uploaded_files = st.file_uploader(
        "📂 Upload documents (PDF)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Uploading documents..."):
            response = requests.post(
                "http://localhost:8000/upload-documents",
                files=[
                    ("files", (file.name, file, "application/pdf"))
                    for file in uploaded_files
                ],
                data={"session_id": st.session_state.session_id}
            )

        if response.status_code == 200:
            st.success("Documents uploaded successfully")
        else:
            st.error("Failed to upload documents")

    st.divider()

    user_input = st.text_area(
        "Paste message / content here",
        height=200,
        placeholder="Ask a question based on uploaded documents"
    )

    run_button = st.button("🚀 Run AI Agent")

    st.divider()

    if st.button("🧹 Reset My Agent Memory"):
        st.session_state.session_id = str(uuid.uuid4())
        st.success("Agent memory reset. New session started.")

# -----------------------------
# THINKING + MEMORY PANEL
# -----------------------------
with col2:
    st.header("🟨 AI Thinking")
    thinking_placeholder = st.empty()

    st.subheader("🧠 Agent Memory (Persistent)")
    memory_placeholder = st.empty()

# -----------------------------
# OUTPUT PANEL
# -----------------------------
with col3:
    st.header("🟩 Output")
    output_container = st.container()

# -----------------------------
# RUN AGENT LOGIC
# -----------------------------
if run_button:

    thinking_placeholder.empty()
    output_container.empty()

    if not user_input.strip():
        st.warning("Please provide a question.")
    else:
        try:
            response = requests.post(
                "http://localhost:8000/process/text",
                json={
                    "input": user_input,
                    "agent_type": agent_type,
                    "session_id": st.session_state.session_id
                },
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Status {response.status_code}: {response.text}")

            result = response.json()

            # -----------------------------
            # AI Thinking (animated)
            # -----------------------------
            thinking_steps = result.get("thinking_steps", [])
            rendered_steps = []

            for step in thinking_steps:
                rendered_steps.append(f"🧠 {step}")
                thinking_placeholder.markdown("\n".join(rendered_steps))
                time.sleep(0.8)

            # -----------------------------
            # Show Memory
            # -----------------------------
            memory = result.get("memory", [])

            if memory:
                memory_text = ""
                for i, msg in enumerate(memory, 1):
                    memory_text += f"**{i}.** {msg}\n\n"
                memory_placeholder.markdown(memory_text)
            else:
                memory_placeholder.caption("No previous memory yet.")

            # -----------------------------
            # Output (DOCUMENT ANSWER)
            # -----------------------------
            with output_container:
                st.success("Action Decision")
                st.write(result.get("action", "No action returned"))

                confidence = float(result.get("confidence", 0))
                st.metric("Confidence", f"{confidence:.2f}")

                if result.get("human_needed"):
                    st.error("⚠️ Escalated to Human")
                else:
                    st.success("✅ Handled Fully by AI")

                st.info(result.get("explanation", "No explanation provided"))

        except Exception as e:
            with output_container:
                st.error("Backend connection failed")
                st.code(str(e))
