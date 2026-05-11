import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="GenAI Chatbot UI", layout="wide")
st.title("GenAI / Agentic AI Chatbot")
st.caption("Upload PDFs and chat with your RAG-enabled backend")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-session-1"


with st.sidebar:
    st.header("Configuration")
    session_id = st.text_input("Session ID", value=st.session_state.session_id)
    st.session_state.session_id = session_id

    use_rag = st.checkbox("Use RAG", value=True)

    st.markdown("---")
    st.subheader("Upload PDF")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if st.button("Upload PDF"):
        if uploaded_file is None:
            st.warning("Please choose a PDF first.")
        else:
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }

                data = {
                    "session_id": st.session_state.session_id
                }

                response = requests.post(
                    f"{BACKEND_URL}/upload-pdf",
                    files=files,
                    data=data,
                    timeout=120
                )

                if response.status_code == 200:
                    st.success("PDF uploaded successfully.")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.write(response.text)
                else:
                    st.error(f"Upload failed: {response.status_code}")
                    st.text(response.text)

            except Exception as e:
                st.error(f"Error while uploading PDF: {e}")


st.subheader("Chat")

for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

user_input = st.chat_input("Ask something about your uploaded documents...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        payload = {
            "user_input": user_input,
            "session_id": st.session_state.session_id,
            "use_rag": use_rag
        }

        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()

            bot_response = (
                data.get("bot_response")
                or data.get("response")
                or data.get("answer")
                or "No response field found in API output."
            )

            st.session_state.chat_history.append(
                {"role": "assistant", "content": bot_response}
            )

            with st.chat_message("assistant"):
                st.markdown(bot_response)

        else:
            error_text = f"Chat failed: {response.status_code} - {response.text}"
            st.session_state.chat_history.append(
                {"role": "assistant", "content": error_text}
            )

            with st.chat_message("assistant"):
                st.error(error_text)

    except Exception as e:
        error_text = f"Error while calling chat API: {e}"
        st.session_state.chat_history.append(
            {"role": "assistant", "content": error_text}
        )

        with st.chat_message("assistant"):
            st.error(error_text)