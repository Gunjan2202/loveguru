import google.generativeai as genai

# Set Gemini API Key
GEMINI_API_KEY = "AIzaSyAfO20CQ88FcStXPhVHkmPmANd2wvAlbf8"
genai.configure(api_key=GEMINI_API_KEY)

# List available models
models = genai.list_models()
for model in models:
    print(model)