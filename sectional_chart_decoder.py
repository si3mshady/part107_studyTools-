import streamlit as st
import boto3
import base64
import json
from PIL import Image
import io

# Initialize AWS Bedrock client
bedrock = boto3.client('bedrock-runtime')

def encode_image(image_file):
    image = Image.open(image_file)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image(image_base64):
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "Analyze this aviation sectional chart. Identify special use airspace like prohibited areas, \
                        restricted areas, warning areas, military operating areas (MOA) military training routes. Give me airspace classes and give me the totals counts. Try to give me airport names if you can but do not make up anything."
                    }
                ]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps(prompt)
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

st.title("Aviation Sectional Chart Analyzer")

uploaded_file = st.file_uploader("Upload an aviation sectional chart image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Sectional Chart", use_column_width=True)
    
    if st.button("Analyze Chart"):
        with st.spinner("Analyzing the chart..."):
            image_base64 = encode_image(uploaded_file)
            analysis_result = analyze_image(image_base64)
        
        st.subheader("Analysis Results:")
        st.text_area("", analysis_result, height=300)