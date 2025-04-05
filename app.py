import streamlit as st
from diffusers import StableDiffusionPipeline
import torch
from datetime import datetime
import os

# Title and UI
st.title("🌸 AI Image Generator")
st.markdown("Generate beautiful images from your imagination ✨")

# Prompt input
prompt = st.text_input("Enter your prompt", "A beautiful fantasy landscape with vivid colors")

# Create folder to save images
output_folder = "generated_images"
os.makedirs(output_folder, exist_ok=True)

# Hugging Face token (add yours here or load from .env / secrets)
HF_TOKEN = "your_huggingface_token_here"  # 🔐 Replace this with your real token

# Load the model once in session
@st.cache_resource
def load_model():
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=HF_TOKEN)
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

pipe = load_model()

# Button to generate
if st.button("✨ Generate Image"):
    with st.spinner("Generating... please wait..."):
        image = pipe(prompt).images[0]
        
        # Save image with timestamp
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(output_folder, filename)
        image.save(filepath)

        # Show image
        st.image(image, caption="Your generated image", use_column_width=True)

        # Download button
        with open(filepath, "rb") as file:
            btn = st.download_button(
                label="⬇️ Download Image",
                data=file,
                file_name=filename,
                mime="image/png"
            )
