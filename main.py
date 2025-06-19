import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import io
import PyPDF2
from streamlit_extras.add_vertical_space import add_vertical_space

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="IMAGE TO CAPTION",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Google API
def initialize_gemini():
    """Initialize Gemini Pro Vision model with API key"""
    try:
        # Get API key from environment or Streamlit secrets
        api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("⚠️ Google API Key not found! Please add it to your .env file or Streamlit secrets.")
            st.info("Get your API key from: https://makersuite.google.com/app/apikey")
            return None
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def get_gemini_response(model, input_text, image_data):
    """Get response from Gemini Pro Vision model"""
    try:
        if input_text:
            response = model.generate_content([input_text, image_data])
        else:
            response = model.generate_content(image_data)
        return response.text
    except Exception as e:
        st.error(f"Error getting Gemini response: {str(e)}")
        return None

def read_pdf_content(pdf_file):
    """Extract text content from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def prepare_image_data(uploaded_file):
    """Prepare image data for Gemini Vision"""
    try:
        # Convert uploaded file to bytes
        bytes_data = uploaded_file.getvalue()
        
        # Create image parts for Gemini
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts[0]
    except Exception as e:
        st.error(f"Error preparing image data: {str(e)}")
        return None

# Main application
def main():
    # Header
    st.title("📸 IMAGE TO CAPTION")
    st.markdown("### Describe Your Images With AI Using Gemini Vision Pro")
    
    # Sidebar for API key setup
    with st.sidebar:
        st.header("🔑 Setup")
        
        # API Key input
        api_key_input = st.text_input(
            "Enter your Google API Key:",
            type="password",
            help="Get your API key from Google AI Studio"
        )
        
        if api_key_input:
            os.environ["GOOGLE_API_KEY"] = api_key_input
            st.success("✅ API Key set successfully!")
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Enter your Google API Key above
        2. Upload an image (JPG, JPEG, PNG)
        3. Optionally add a custom prompt
        4. Click 'Generate Caption' to get AI description
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Use Cases")
        st.markdown("""
        - **Social Media**: Generate engaging captions
        - **Content Creation**: Describe images for blogs
        - **Accessibility**: Create alt text for images
        - **E-commerce**: Product descriptions
        """)
    
    # Initialize Gemini model
    model = initialize_gemini()
    
    if model is None:
        st.warning("Please configure your Google API Key to continue.")
        return
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload & Configure")
        
        # Custom prompt input
        input_prompt = st.text_area(
            "Custom Prompt (Optional):",
            placeholder="e.g., 'Describe this image for social media', 'Create a creative caption', 'What's happening in this image?'",
            height=100
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image to generate captions"
        )
        
        # Quick prompt buttons
        st.markdown("#### 🚀 Quick Prompts")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📱 Social Media Caption"):
                input_prompt = "Create an engaging social media caption for this image"
        
        with col_btn2:
            if st.button("🎨 Creative Description"):
                input_prompt = "Provide a creative and detailed description of this image"
        
        col_btn3, col_btn4 = st.columns(2)
        
        with col_btn3:
            if st.button("🛍️ Product Description"):
                input_prompt = "Create a product description based on this image"
        
        with col_btn4:
            if st.button("♿ Alt Text"):
                input_prompt = "Generate accessibility alt text for this image"
    
    with col2:
        st.header("🖼️ Image Preview")
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Image details
            st.markdown("**Image Details:**")
            st.write(f"- **Filename:** {uploaded_file.name}")
            st.write(f"- **File size:** {uploaded_file.size} bytes")
            st.write(f"- **Dimensions:** {image.size[0]} x {image.size[1]} pixels")
            st.write(f"- **Format:** {image.format}")
        else:
            st.info("👆 Please upload an image to see preview")
    
    # Generate caption section
    if uploaded_file is not None:
        add_vertical_space(2)
        
        st.header("🎯 Generate Caption")
        
        col_gen1, col_gen2, col_gen3 = st.columns([1, 1, 1])
        
        with col_gen1:
            generate_button = st.button(
                "🚀 Generate Caption",
                type="primary",
                use_container_width=True
            )
        
        with col_gen2:
            one_phrase_button = st.button(
                "📝 Give me caption in one phrase",
                use_container_width=True
            )
        
        with col_gen3:
            detailed_button = st.button(
                "📚 Detailed Analysis",
                use_container_width=True
            )
        
        # Process the image and generate caption
        if generate_button or one_phrase_button or detailed_button:
            with st.spinner("🤖 AI is analyzing your image..."):
                try:
                    # Prepare image data
                    image_data = prepare_image_data(uploaded_file)
                    
                    if image_data:
                        # Set prompt based on button clicked
                        if one_phrase_button:
                            prompt = "Give me the caption in one phrase"
                        elif detailed_button:
                            prompt = "Provide a detailed analysis and description of this image, including objects, people, setting, mood, and any notable details"
                        else:
                            prompt = input_prompt if input_prompt else "Describe this image in detail"
                        
                        # Get response from Gemini
                        response = get_gemini_response(model, prompt, image_data)
                        
                        if response:
                            st.success("✅ Caption generated successfully!")
                            
                            # Display results
                            st.header("📋 Generated Caption")
                            
                            # Create a nice formatted output
                            st.markdown(f"""
                            <div style="
                                background-color: #f0f2f6;
                                padding: 20px;
                                border-radius: 10px;
                                border-left: 5px solid #1f77b4;
                                margin: 10px 0;
                            ">
                                <h4 style="margin-top: 0; color: #1f77b4;">🎯 AI Generated Caption:</h4>
                                <p style="font-size: 16px; line-height: 1.6; margin-bottom: 0;">{response}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Copy to clipboard functionality
                            st.text_area(
                                "Copy this caption:",
                                value=response,
                                height=100,
                                help="Select all text and copy (Ctrl+A, Ctrl+C)"
                            )
                            
                        else:
                            st.error("Failed to generate caption. Please try again.")
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Footer
    add_vertical_space(3)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🤖 Powered by Google Gemini Vision Pro | Built with Streamlit</p>
        <p>Perfect for social media managers, content creators, and accessibility needs!</p>
    </div>
    """, unsafe_allow_html=True)

# Additional utility functions
def create_env_file():
    """Create a sample .env file"""
    env_content = """# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# App Configuration  
APP_NAME=AI Image Captioning App
DEBUG=False
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)

def setup_instructions():
    """Display setup instructions"""
    st.markdown("""
    ## 🚀 Setup Instructions
    
    ### 1. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
    
    ### 2. Get Google API Key
    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Create a new API key
    3. Copy the API key
    
    ### 3. Configure Environment
    1. Create a `.env` file in your project directory
    2. Add your API key:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```
    
    ### 4. Run the Application
    ```bash
    streamlit run main.py
    ```
    
    ### 5. Deploy to Streamlit Cloud
    1. Push your code to GitHub
    2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
    3. Add your API key to Streamlit secrets
    """)

if __name__ == "__main__":
    main()