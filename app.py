import streamlit as st
import os
import io
from PIL import Image
import google.generativeai as genai
from google.generativeai import types
from google.api_core import retry

# Configure API key
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Define retry handler for content generation
is_retriable = lambda e: (hasattr(e, 'code') and e.code in {429, 503})
genai.GenerativeModel.generate_content = retry.Retry(predicate=is_retriable)(genai.GenerativeModel.generate_content)

# Streamlit UI
st.title("Cute AI Image Generator 💖")
st.write("Enter your dreamy prompt below and let's make some GenAI magic ✨")

character = st.text_input("Character", value="naruto")
style = st.text_input("Style", value="realistic")
scene = st.text_input("Scene", value="sunset behind the hills, palm trees")

if st.button("Generate Image"):
    prompt = f"Can you create a {style} image of {character} couple in a {scene}?"

    with st.spinner("Cooking up your masterpiece... 🎨"):
        try:
            model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp-image-generation")
            response = model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(response_mime_type="image/png"),
                stream=False
            )

            image_data = None
            for part in response.parts:
                if hasattr(part, 'inline_data'):
                    image_data = part.inline_data.data
                    break

            if image_data:
                file_path = "generated_image.png"
                with open(file_path, "wb") as f:
                    f.write(image_data)
                st.success("Image generated successfully and saved! 💾")
                with open(file_path, "rb") as f:
                    st.download_button("Download Image", f, file_name="generated_image.png", mime="image/png")
            else:
                st.error("No image data found in response 😓")

        except Exception as e:
            st.error(f"Error during image generation: {e}")
