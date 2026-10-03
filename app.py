import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# Configuration
MODEL_NAME = "gemini-2.5-flash"
st.set_page_config(page_title="Snap & Study", page_icon="📚")


def get_required_secret(secret_name, env_name=None):
    value = st.secrets.get(secret_name) if hasattr(st, "secrets") else None
    if value is None and env_name:
        value = os.getenv(env_name)
    if value is None:
        raise RuntimeError(f"Missing required secret: {secret_name}")
    return value


# Retrieve secrets
GEMINI_API_KEY = get_required_secret("GEMINI_API_KEY", "GEMINI_API_KEY")
GMAIL_ADDRESS = get_required_secret("GMAIL_ADDRESS", "GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = get_required_secret("GMAIL_APP_PASSWORD", "GMAIL_APP_PASSWORD").replace(" ", "")


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def send_email(to_address, subject, body):
    """Sends a study digest email using Gmail SMTP and an App Password."""
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject

        # Attach the formatted plain text email body
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SSL SMTP port (465)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return True, "Email sent successfully!"
    except Exception as error:
        return False, str(error)


# Step 1: Onboarding Screen
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap your notes or diagrams. Understand concepts. Email yourself study digests.")

    with st.form("onboarding_form"):
        name = st.text_input("Your Name")
        email_address = st.text_input(
            "Email Address",
            placeholder="student@example.com",
            help="Your study digests will be sent to this email address.",
        )
        submitted = st.form_submit_button("Let's Study 🚀")

    if submitted:
        if not name.strip() or not email_address.strip():
            st.warning("Please fill in both your name and email address.")
        elif "@" not in email_address or "." not in email_address:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email_address = email_address.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

# Step 2: Main Study Chat Interface
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 Snap & Study")

with button_col:
    has_study_content = any(
        message["role"] == "user" for message in st.session_state.messages
    )
    if st.button(
        "📤 Send to Email",
        disabled=not has_study_content,
        help=(
            None
            if has_study_content
            else "Ask a question or upload a photo of your notes first."
        ),
        use_container_width=True,
    ):
        with st.spinner("Preparing your study digest..."):
            summary_raw = ask_gemini([SUMMARY_REQUEST_PROMPT])

            # Extract subject line if generated, or use default
            lines = summary_raw.split("\n")
            subject = "Your Snap & Study Digest"
            body = summary_raw

            if lines and lines[0].startswith("Subject:"):
                subject = lines[0].replace("Subject:", "").strip()
                body = "\n".join(lines[1:]).strip()

            success, info = send_email(st.session_state.email_address, subject, body)

        if success:
            st.success("Sent! Check your inbox 📧")
        else:
            st.error(f"Couldn't send email: {info}")

st.caption(f"Logged in as {st.session_state.name} — digests send to {st.session_state.email_address}")

# Show welcome message or render conversation history
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE)
else:
    for message in st.session_state.messages:
        render_message(message)

# User Chat & Photo Input
user_input = st.chat_input(
    "Ask a question, or attach a photo of your notes/diagram",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("Please analyze this study material and break down the core concepts step-by-step.")

    with st.spinner("Analyzing notes..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
    st.rerun()