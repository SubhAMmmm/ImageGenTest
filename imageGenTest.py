import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image, ImageEnhance
import io
import time
import sqlite3

# Set up the Hugging Face Inference Client
client = InferenceClient("stabilityai/stable-diffusion-3.5-large-turbo", token="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")

# Set up SQLite database
conn = sqlite3.connect("user_data.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS user_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    design_description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Streamlit app configuration
st.set_page_config(page_title="Personalized Name Image Generator", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better styling
st.markdown("""
<style>
.big-title {
    font-size: 36px;
    color: #2c3e50;
    text-align: center;
    margin-bottom: 20px;
}
.subtitle {
    color: #7f8c8d;
    text-align: center;
}
.loading-spinner {
    font-size: 18px;
    color: #2c3e50;
    text-align: center;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<h1 class="big-title">✨ Personalized Name Image Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create a stunning 1080x1080 image of your name in a unique style</p>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns(2)

with col1:
    # Name Input
    user_name = st.text_input("Enter Your Name", placeholder="e.g., Alexander")

with col2:
    # Style Description Input
    design_description = st.text_input(
        "Describe Your Desired Design Style", 
        placeholder="e.g., glowing neon typography, elegant glass text, watercolor effect"
    )

# Generate Image Button
if st.button("Generate My Name Image", type="primary"):
    if user_name and design_description:
        # Store user input in database
        c.execute("INSERT INTO user_inputs (name, design_description) VALUES (?, ?)", (user_name, design_description))
        conn.commit()

        # Construct enhanced prompt
        prompt = (
            f"A magical and vibrant 1080x1080 composition prominently featuring the name '{user_name}' in 3D, "
            f"styled in a {design_description} theme. Ensure the text '{user_name}' is clearly visible, "
            f"centered, and seamlessly integrated into the theme. Include iconic elements and artistic patterns "
            f"associated with {design_description}, ensuring a whimsical, enchanting, and cinematic quality. "
            f"Use 3D fonts and typography that complement the {design_description} theme, ensuring text '{user_name}' harmonizes beautifully with the background. "
            f"Ultra-realistic rendering, vivid color palette, dynamic lighting, intricate details, polished for perfection, "
            f"trending on ArtStation."
        )

        try:
            # Status message
            with st.spinner('Generating your personalized image...'):
                # Simulate loading for handling too many requests
                with st.empty():
                    for _ in range(10):  # Rotating animation
                        st.markdown('<p class="loading-spinner">Please wait, your image is being generated...</p>', unsafe_allow_html=True)
                        time.sleep(0.5)

                # Generate the image
                image = client.text_to_image(prompt)

                # Resize and enhance the image
                resized_image = image.resize((1080, 1080), Image.LANCZOS)
                enhancer = ImageEnhance.Sharpness(resized_image)
                enhanced_image = enhancer.enhance(2.0)  # Sharpen for better clarity

                # Display the image
                st.image(enhanced_image, caption=f"Generated Image: {user_name} with your style", use_column_width=True)

                # Save the image in-memory for download
                image_buffer = io.BytesIO()
                enhanced_image.save(image_buffer, format="PNG", quality=95)
                image_buffer.seek(0)

                # Download button
                st.download_button(
                    label="Download Image", 
                    data=image_buffer, 
                    file_name=f"{user_name}_NameImage_1080x1080.png", 
                    mime="image/png"
                )

        except Exception as e:
            if "429 Client Error" in str(e):
                st.warning("The service is currently overloaded. Please wait a moment and try again.")
            else:
                st.error(f"Error generating image: {e}")
    else:
        st.warning("Please enter your name and describe your design style")

# Side panel for database display
with st.sidebar:
    st.markdown("## Denominate")
    if st.checkbox("Denominative detail"):
        password = st.text_input("Enter Password", type="password")
        correct_password = "secure123"  # Replace with your desired password

        if password:
            if password == correct_password:
                c.execute("SELECT name, design_description, timestamp FROM user_inputs ORDER BY timestamp DESC")
                rows = c.fetchall()
                if rows:
                    for row in rows:
                        st.markdown(f"- **Name**: {row[0]} | **Design**: {row[1]} | **Timestamp**: {row[2]}")
                else:
                    st.info("No data available.")
            else:
                st.error("Incorrect password. Please try again.")

# Footer
st.markdown("---")
st.markdown("*Powered by Stable Diffusion 3.5 Large Turbo | Create unique name art*")
