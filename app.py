import streamlit as st
import os
import base64
import io
from PIL import Image
from google import genai
from google.genai import types
from google.api_core import retry

# Setup page config
st.set_page_config(
    page_title="Gemini Image Generator",
    page_icon="🎨",
    layout="wide"
)

# CSS to improve the app's appearance
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .download-btn {
        margin-top: 1rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("AI Image Generator")
st.subheader("Create custom images with Google's Gemini 2.0")

# Setup API key input
api_key = st.text_input("Enter your Google API Key:", type="password")

# Initialize Gemini Client when API key is provided
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        # Add retry functionality for API rate limits
        is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
        genai.models.Models.generate_content = retry.Retry(
            predicate=is_retriable)(genai.models.Models.generate_content)
        
        st.success("API key set successfully!")
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        client = None
else:
    st.warning("Please enter your Google API key to continue")
    client = None

# Create columns for input
col1, col2 = st.columns(2)

with col1:
    # Input fields
    character = st.text_input("Character or Subject:", placeholder="naruto, astronaut, tiger, etc.")
    style = st.selectbox("Image Style:", 
                        options=["realistic", "anime", "digital art", "watercolor", "oil painting", 
                                "pencil sketch", "pixel art", "3D render", "minimalist", "cartoon"])
    scene = st.text_area("Scene Description:", 
                        placeholder="sunset behind the hills, urban cyberpunk city, enchanted forest, etc.",
                        height=100)

# Function to generate and save image
def generate_image():
    if not all([character, style, scene]):
        st.warning("Please fill in all fields")
        return None
    
    with st.spinner("Generating your image... This may take a moment."):
        try:
            generation_prompt = f"Create a {style} image of {character} in a {scene}. Make it detailed and visually striking."
            
            generation_response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=generation_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['text', 'image']
                )
            )
            
            image_bytes = None
            image_description = ""
            
            for part in generation_response.candidates[0].content.parts:
                if part.text:
                    image_description = part.text
                elif part.inline_data:
                    image_bytes = part.inline_data.data
            
            if image_bytes:
                # Save image to a file in the uploads directory
                if not os.path.exists("generated_images"):
                    os.makedirs("generated_images")
                
                # Create a unique filename based on the prompt
                filename = f"gemini_{character.replace(' ', '_')}_{style.replace(' ', '_')}.png"
                filepath = os.path.join("generated_images", filename)
                
                # Save the image
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                return {
                    "bytes": image_bytes,
                    "filepath": filepath,
                    "filename": filename,
                    "description": image_description
                }
            else:
                st.error("No image was generated. Please try again with a different prompt.")
                return None
                
        except Exception as e:
            st.error(f"Error generating image: {e}")
            return None

# Generate button
if client and st.button("Generate Image", type="primary", use_container_width=True):
    image_data = generate_image()
    
    if image_data:
        # Display the generated image and download button
        with col2:
            st.image(image_data["bytes"], caption=f"{style.title()} image of {character}")
            
            # Create download button
            st.download_button(
                label="Download Image",
                data=image_data["bytes"],
                file_name=image_data["filename"],
                mime="image/png",
                key="download_button",
                use_container_width=True
            )
            
            # Show the saved location
            st.success(f"Image saved locally at: {image_data['filepath']}")
            
            # Show description if available
            if image_data["description"]:
                st.write("Image Description:")
                st.write(image_data["description"])

# Add information about the app
st.markdown("---")
st.markdown("""
### About this App
This application uses Google's Gemini 2.0 to generate images based on your descriptions.
- Enter a character or subject
- Select an art style
- Describe the scene or background
- Click Generate to create your image
- Download the generated image for your use

Note: You need your own Google API key with access to Gemini 2.0 image generation.
""")
