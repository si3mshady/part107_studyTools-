import streamlit as st
import boto3
import json

# Initialize AWS Bedrock client
bedrock = boto3.client('bedrock-runtime')

def analyze_metar_taf(input_string):
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Decode and explain the following METAR or TAF in detail, breaking down each component:\n\n{input_string}\n\nProvide a comprehensive explanation of what each part means, including information about wind, visibility, weather conditions, temperature, dew point, and any other relevant information contained in the METAR or TAF."
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

st.title("METAR/TAF Decoder")

st.write("Enter a METAR or TAF string to decode and explain its components.")

input_string = st.text_input("METAR or TAF String", "")

if st.button("Decode"):
    if input_string:
        with st.spinner("Decoding..."):
            decoded_result = analyze_metar_taf(input_string)
        
        st.subheader("Decoded Explanation:")
        st.markdown(decoded_result)
    else:
        st.warning("Please enter a METAR or TAF string to decode.")