from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import pdfplumber
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure the Google Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Set up the GenerativeModel using Gemini 1.5 Flash
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to get a response from the Gemini model
def get_gemini_response(input_text, additional_data, prompt):
    response = model.generate_content([input_text, additional_data[0], prompt])
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

# Function to extract text from a PDF file
def extract_pdf_text(uploaded_file):
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                pdf_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            return pdf_text
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {e}")
    else:
        raise FileNotFoundError("No PDF uploaded")

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
card_color = "#FFFFFF"
border_color = "#E0E0E0"

# Custom CSS for advanced styling
st.markdown(f"""
    <style>
    .stApp {{
        padding: 20px;
    }}
    .main-container {{
        max-width: 900px;
        margin: auto;
        background-color: {card_color};
        border: 1px solid {border_color};
        border-radius: 15px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        padding: 30px;
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
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {secondary_color} !important;
    }}
    .stFileUploader {{
        color: {secondary_color} !important;
        font-size: 16px;
    }}
    .css-1cpxqw2 {{
        font-size: 24px;
    }}
    .footer {{
        text-align: center;
        color: {primary_color};
        font-size: 16px;
        margin-top: 50px;
    }}
    .response-container {{
        background-color: {card_color};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Invoice Extractor Tool")
st.markdown("<p style='font-size:18px;'>Upload an invoice image or PDF and ask any question.</p>", unsafe_allow_html=True)

input_text = st.text_input("Input Prompt", placeholder="Enter your question here...", key="input_prompt")
uploaded_file = st.file_uploader("Upload Invoice (JPG/PNG/PDF)", type=["jpg", "jpeg", "png", "pdf"], label_visibility="visible")

# Example input guide
st.info("Example questions: \n- What is the total amount?\n- Who is the buyer?\n- When is the payment due?", icon="ℹ️")

submit = st.button("Analyze Invoice", key="submit_button")

# Display the uploaded file if any
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.markdown("<h3>Uploaded PDF File:</h3>", unsafe_allow_html=True)
        pdf_display = BytesIO(uploaded_file.getvalue())
        st.download_button(
            label="View PDF",
            data=pdf_display,
            file_name=uploaded_file.name,
            mime="application/pdf"
        )
    else:
        st.image(uploaded_file, caption="Uploaded Invoice Image", use_container_width=True)

# Default prompt for the Gemini model
input_prompt = """
    You are an expert in understanding invoices. You will receive invoice data (images or text) and answer any questions based on the provided data.
"""

# Trigger the model when the button is clicked
if submit and uploaded_file is not None and input_text:
    try:
        if uploaded_file.type == "application/pdf":
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_pdf_text(uploaded_file)
            response = get_gemini_response(input_text, [pdf_text], input_prompt)
        else:
            image_data = input_image_setup(uploaded_file)
            with st.spinner("Processing the invoice image..."):
                response = get_gemini_response(input_text, image_data, input_prompt)

        st.markdown("<div class='response-container'>", unsafe_allow_html=True)
        st.subheader("Response")
        st.success(response)  # Display the model's response in a success box
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    if not uploaded_file and submit:
        st.error("Please upload a file to proceed.")
    if not input_text and submit:
        st.error("Please enter a valid prompt.")

# Footer with branding or additional instructions
st.markdown(
    f"""
    <div class='footer'>
    <hr>
    <p>Developed by Hamza | Powered by Gemini 1.5 Flash</p>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
