import google.generativeai as genai



# List available models
models = genai.list_models()
for model in models:
    print(model)