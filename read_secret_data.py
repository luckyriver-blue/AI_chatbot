import streamlit as st
import os

openai_key = os.environ["OPENAI_API_KEY"]

firebase_project_settings = {
  "type": "service_account",
  "project_id": "chatbot-e8214",
  "private_key_id": os.environ["PRIVATE_KEY_ID"],
  "private_key": os.environ["PRIVATE_KEY"].replace(r'\n', '\n'),
  "client_email": os.environ["CLIENT_EMAIL"],
  "client_id": os.environ["CLIENT_ID"],
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
}
