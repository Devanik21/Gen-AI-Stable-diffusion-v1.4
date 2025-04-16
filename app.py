import streamlit as st
from PIL import Image
from io import BytesIO
import google.generativeai as genai

# Load your Google API key securely 💫
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp-image-generation"
)

st.set_page_config(page_title="Gemini Image Generator", page_icon="🎨")
st.title("🎨 Gemini Image Generator")
st.write("Describe your idea and watch it come to life ✨")

# Prompt input
user_prompt = st.text_input("Enter your prompt below:")

if st.button("Generate Image ✨") and user_prompt:
    with st.spinner("Generating your magical image..."):
        generation_response = model.generate_content(
            contents=user_prompt,
            generation_config={"response_mime_type": ["text", "image"]}
        )

        image_bytes = None
        description = ""

        for part in generation_response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                description += part.text
            elif hasattr(part, "inline_data") and part.inline_data:
                image_bytes = part.inline_data.data

        if image_bytes:
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption="Generated Image ✨", use_column_width=True)

            # Download button
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            st.download_button(
                label="💾 Download Image",
                data=buffered.getvalue(),
                file_name="generated_image.png",
                mime="image/png"
            )
        else:
            st.error("Oops! No image was generated. Try a different prompt?")

    if description:
        st.markdown("**Model Notes:**")
        st.write(description)
