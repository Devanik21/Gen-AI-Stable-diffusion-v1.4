import streamlit as st
from PIL import Image
from io import BytesIO
import google.generativeai as genai

# Configure Gemini with your API key securely 🔐
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Load the Gemini image generation model
model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

st.set_page_config(page_title="Gemini Image Generator", page_icon="🎨")
st.title("🎨 Gemini Image Generator")
st.write("Describe your idea and let Gemini paint it into reality ✨")

# Prompt input
user_prompt = st.text_input("📝 Enter your image prompt:")

if st.button("✨ Generate Image") and user_prompt:
    with st.spinner("Crafting your visual masterpiece..."):
        try:
            # Just pass the prompt — no special configs needed!
            generation_response = model.generate_content(user_prompt)

            image_bytes = None
            for part in generation_response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_bytes = part.inline_data.data

            if image_bytes:
                image = Image.open(BytesIO(image_bytes))
                st.image(image, caption="🖼️ Your Generated Image", use_column_width=True)

                # Prepare download
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                st.download_button(
                    label="💾 Download Image",
                    data=buffered.getvalue(),
                    file_name="gemini_generated.png",
                    mime="image/png"
                )
            else:
                st.error("Hmm... No image came back. Wanna try a different prompt?")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
