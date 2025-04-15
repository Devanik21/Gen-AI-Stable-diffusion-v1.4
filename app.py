import streamlit as st
import os
import base64
import io
from PIL import Image
import google.generativeai as genai
from google.generativeai import types
from google.api_core import retry

# Configure your API key from Streamlit secrets or environment variables.
api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Set up retry for the image generation function if needed.
is_retriable = lambda e: (hasattr(e, 'code') and e.code in {429, 503})
# Depending on the API, you might wrap calls in a retry loop. Here, we call the function directly.

st.title("Cute Image Generator")
st.write("Enter the details below to generate your forward-thinking image!")

# Get user input
character = st.text_input("Enter character", value="naruto")
style = st.text_input("Enter style", value="realistic")
scene = st.text_input("Enter scene", value="sunset behind the hills, palm trees")

if st.button("Generate Image"):
    generation_prompt = f"Can you create a {style} image of {character} couple in a {scene}?"
    with st.spinner("Generating your image, please wait..."):
        try:
            # Call the image generation API using the updated google.generativeai method.
            # Adjust the parameters as per your model's documentation.
            generation_response = genai.generate_image(
                prompt=generation_prompt,
                model="gemini-2.0-flash-exp-image-generation"
            )
            # Assume the response has an attribute `image_bytes` containing the image data.
            image_bytes = getattr(generation_response, "image_bytes", None)
        except Exception as e:
            st.error(f"Error during image generation: {e}")
            image_bytes = None

    if image_bytes is not None:
        # Save the image to a file for later download.
        image_file = "generated_image.png"
        with open(image_file, "wb") as f:
            f.write(image_bytes)
        st.success("Image generated and saved as generated_image.png!")
        # Provide a download button for the saved image.
        with open(image_file, "rb") as f:
            st.download_button("Download Image", data=f, file_name=image_file, mime="image/png")
    else:
        st.error("No image was generated. Please try again!")
