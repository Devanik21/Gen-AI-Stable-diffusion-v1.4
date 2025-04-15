import streamlit as st
import os
import io
from PIL import Image
import google.generativeai as genai
from google.generativeai import types
from google.api_core import retry

# Configure your API key
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Optional retry setup (not strictly necessary here)
is_retriable = lambda e: (hasattr(e, 'code') and e.code in {429, 503})
genai.GenerativeModel.generate_content = retry.Retry(predicate=is_retriable)(genai.GenerativeModel.generate_content)

st.title("✨ GenAI Image Generator")
st.write("Create magical images with your imagination 💖")

# Inputs
character = st.text_input("Character", value="naruto")
style = st.text_input("Style", value="realistic")
scene = st.text_input("Scene", value="sunset behind the hills, palm trees")

if st.button("Generate Image"):
    prompt = f"Can you create a {style} image of {character} couple in a {scene}?"

    with st.spinner("Summoning your GenAI artwork... 🧚‍♀️"):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
            response = model.generate_content(prompt, stream=False)

            image_data = None
            for part in response.parts:
                if hasattr(part, "inline_data") and hasattr(part.inline_data, "data"):
                    image_data = part.inline_data.data
                    break

            if image_data:
                file_path = "generated_image.png"
                with open(file_path, "wb") as f:
                    f.write(image_data)

                st.success("Yay! Image saved 💾")
                with open(file_path, "rb") as f:
                    st.download_button("Download Image", f, file_name="generated_image.png", mime="image/png")
            else:
                st.error("Hmm... no image returned. Try another prompt maybe? 🥺")

        except Exception as e:
            st.error(f"Oopsie! Something went wrong: {e}")
