from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Google Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Set up the GenerativeModel using Gemini 1.5 Flash
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to get a response from the Gemini model
def get_gemini_response(input_text, image_data, prompt):
    response = model.generate_content([input_text, image_data[0], prompt])
    return response.text

# Function to prepare the uploaded image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Extract MIME type
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize Streamlit app with custom page configurations
st.set_page_config(
    page_title="Advanced Multi-Language Invoice Extractor",
    page_icon=":receipt:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define a color palette for the app
primary_color = "#4CAF50"
secondary_color = "#FF6F61"
background_color = "#F4F4F4"

# Custom CSS for better style
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color};
    }}
    .css-1d391kg {{
        color: {primary_color} !important;
    }}
    .stButton > button {{
        background-color: {primary_color} !important;
        color: white;
        border-radius: 10px;
        border: none;
        font-size: 18px;
        padding: 10px 20px;
    }}
    .stFileUploader {{
        color: {secondary_color} !important;
    }}
    .css-1cpxqw2 {{
        font-size: 24px;
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar for user inputs and image upload
with st.sidebar:
    st.title("Invoice Extractor Tool")
    st.markdown("Upload an invoice image and ask any question.")
    
    input_text = st.text_input("Input Prompt", key="input_prompt")
    uploaded_file = st.file_uploader("Upload Invoice (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    # Example input guide
    st.info("Example questions: \n- What is the total amount?\n- Who is the buyer?\n- When is the payment due?", icon="ℹ️")
    
    submit = st.button("Analyze Invoice", key="submit_button")

# Display the uploaded image if any
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Invoice Image", use_column_width=True)

# Default prompt for the Gemini model
input_prompt = """
    You are an expert in understanding invoices. You will receive images of invoices and answer any questions based on the image.
"""

# Trigger the model when the button is clicked
if submit and uploaded_file is not None and input_text:
    try:
        image_data = input_image_setup(uploaded_file)
        with st.spinner("Processing the invoice..."):
            response = get_gemini_response(input_text, image_data, input_prompt)
        st.subheader("Response")
        st.success(response)  # Display the model's response in a success box

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    if not uploaded_file and submit:
        st.error("Please upload an image to proceed.")
    if not input_text and submit:
        st.error("Please enter a valid prompt.")

# Footer with branding or additional instructions
st.markdown(
    f"""
    <hr>
    <p style='text-align: center; color: {primary_color}; font-size: 16px;'>
    Developed by Hamza | Powered by Gemini 1.5 Flash
    </p>
    """, unsafe_allow_html=True
)
