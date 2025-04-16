import streamlit as st
from PIL import Image
from io import BytesIO
import google.generativeai as genai

# Secure API key setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Use the dedicated image generation model
model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

st.set_page_config(page_title="Gemini Image Generator", page_icon="🖼️")
st.title("🎨 Gemini Image Generator")
st.write("Enter a creative prompt and let Gemini turn it into art ✨")

# Prompt input
user_prompt = st.text_input("💡 Your image prompt:")

if st.button("Generate 🪄") and user_prompt:
    with st.spinner("Generating your image... hang tight!"):
        try:
            response = model.generate_content(user_prompt)

            # Attempt to grab inline image data
            image_data = None
            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data

            if image_data:
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="Here’s your masterpiece! 🖼️", use_column_width=True)

                # Allow download
                buf = BytesIO()
                image.save(buf, format="PNG")
                st.download_button("💾 Download", data=buf.getvalue(), file_name="gemini_image.png", mime="image/png")
            else:
                st.error("Hmm... No image was generated. Try being more specific or imaginative 💭")
        except Exception as e:
            st.error(f"Yikes! Something went wrong: {e}")
