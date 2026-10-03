# Snap & Study

Snap & Study is a Streamlit study assistant. Ask questions or upload an image of your notes, a textbook page, or a diagram to get a step-by-step explanation from Gemini. You can also email a study digest to yourself.

## Features

- Chat with an AI study tutor.
- Upload JPG, JPEG, or PNG images for analysis.
- Generate and email a study digest of the current conversation.

## Requirements

- Python 3.10 or newer.
- A Google Gemini API key.
- A Gmail account with 2-Step Verification enabled and a Gmail App Password, if you want to use email digests.

## Run locally

Open a terminal in the project folder and create a virtual environment:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the dependencies and start the app:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually [http://localhost:8501](http://localhost:8501). Keep the terminal open while using the app.

If PowerShell does not recognize `python`, try `py` in the commands above. You can also run the app without activating the environment:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Configure secrets

The app needs these three secrets:

- `GEMINI_API_KEY`: a Gemini API key.
- `GMAIL_ADDRESS`: the Gmail address used to send digests.
- `GMAIL_APP_PASSWORD`: an App Password for that Gmail account, not your regular account password.

For local use, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the placeholder values:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-gmail-app-password"
```

Do not commit `.streamlit/secrets.toml`, API keys, or passwords. The real secrets file is excluded by `.gitignore`.

## Deploy with Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Create an app in [Streamlit Community Cloud](https://share.streamlit.io/) and select the repository, branch, and `app.py` as the main file.
3. Open the app's **Settings → Secrets** and add the secrets in TOML format:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-gmail-app-password"
   ```

4. Save the settings and allow the app to deploy.

The dependency manifest is `requirements.txt`; Streamlit Cloud uses it to install the Python packages.

## Usage

1. Enter your name and the email address that should receive study digests.
2. Ask a study question or upload an image in the chat input.
3. After adding study content, select **Send to Email** to generate and send a digest.

## Project files

- `app.py` — Streamlit application and Gemini/Gmail integrations.
- `prompts.py` — Tutor, welcome, and study-digest prompts.
- `requirements.txt` — Python dependencies.
- `.streamlit/secrets.toml.example` — Safe template for local secrets configuration.
