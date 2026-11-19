import os
import streamlit as st
from dataclasses import dataclass

@dataclass
class Settings:
    groq_api_key: str
    groq_model: str

def get_settings() -> Settings:
    key = None
    model = None

    # Streamlit Community Cloud: configure these in App > Settings > Secrets.
    try:
        key = st.secrets.get("GROQ_API_KEY")
        model = st.secrets.get("GROQ_MODEL")
    except Exception:
        pass

    # Local development fallback.
    key = key or os.getenv("GROQ_API_KEY")
    model = model or os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"

    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to .streamlit/secrets.toml "
            "locally or Streamlit Community Cloud → App settings → Secrets."
        )

    return Settings(groq_api_key=key, groq_model=model)
