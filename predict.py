import datetime
import streamlit as st
from langgraph.graph import StateGraph
from langchain.chat_models import ChatOpenAI
from typing import TypedDict

# Define State Schema
class PredictionState(TypedDict):
    dob: str
    zodiac_sign: str
    numerology_number: int
    prediction: str

# Initialize GPT-4 Model
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key="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")


# Function to calculate Zodiac Sign
def get_zodiac(state: PredictionState) -> PredictionState:
    dob = datetime.datetime.strptime(state["dob"], "%d-%m-%Y")
    
    zodiac_dates = [
        ("Capricorn", (12, 22), (1, 19)), ("Aquarius", (1, 20), (2, 18)),
        ("Pisces", (2, 19), (3, 20)), ("Aries", (3, 21), (4, 19)),
        ("Taurus", (4, 20), (5, 20)), ("Gemini", (5, 21), (6, 20)),
        ("Cancer", (6, 21), (7, 22)), ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)), ("Libra", (9, 23), (10, 22)),
        ("Scorpio", (10, 23), (11, 21)), ("Sagittarius", (11, 22), (12, 21))
    ]
    
    for sign, start, end in zodiac_dates:
        if (dob.month == start[0] and dob.day >= start[1]) or (dob.month == end[0] and dob.day <= end[1]):
            state["zodiac_sign"] = sign
            break
    
    return state

# Function to calculate Numerology Number
def get_numerology(state: PredictionState) -> PredictionState:
    digits = [int(digit) for digit in state["dob"] if digit.isdigit()]
    numerology_number = sum(digits)
    
    while numerology_number > 9 and numerology_number not in [11, 22, 33]:  # Master numbers
        numerology_number = sum(int(digit) for digit in str(numerology_number))
    
    state["numerology_number"] = numerology_number
    return state

# Function to predict future
def predict_future(state: PredictionState) -> PredictionState:
    prompt = (
        f"You are an expert astrologer and numerologist. "
        f"Predict the future of a person born on {state['dob']}. "
        f"Their Zodiac sign is {state['zodiac_sign']} and their Numerology number is {state['numerology_number']}. "
        f"Provide a detailed, insightful prediction."
    )
    
    state["prediction"] = llm.predict(prompt)
    return state

# Build the LangGraph
graph = StateGraph(PredictionState)

# Add nodes
graph.add_node("get_zodiac", get_zodiac)
graph.add_node("get_numerology", get_numerology)
graph.add_node("predict_future", predict_future)

# Define flow
graph.set_entry_point("get_zodiac")
graph.add_edge("get_zodiac", "get_numerology")
graph.add_edge("get_numerology", "predict_future")

# Compile the graph
graph = graph.compile()

# ========================= UI using Streamlit =========================

st.set_page_config(page_title="🔮 Future Prediction Chatbot", layout="centered")

st.title("🔮 Future Prediction Chatbot")
st.subheader("Enter your birth details to see what the future holds!")

# User Input
dob_input = st.text_input("📅 Enter your Date of Birth (DD-MM-YYYY)", "")

if st.button("🔍 Predict My Future"):
    if dob_input:
        try:
            # Validate Date Format
            datetime.datetime.strptime(dob_input, "%d-%m-%Y")

            # Run prediction
            initial_state = PredictionState(dob=dob_input, zodiac_sign="", numerology_number=0, prediction="")
            result = graph.invoke(initial_state)

            # Display Results
            st.success(f"🔮 **Zodiac Sign:** {result['zodiac_sign']}")
            st.success(f"🔢 **Numerology Number:** {result['numerology_number']}")
            st.markdown(f"📜 **Prediction:**\n\n{result['prediction']}")

        except ValueError:
            st.error("⚠️ Please enter a valid date in DD-MM-YYYY format!")
    else:
        st.warning("⚠️ Please enter your Date of Birth.")
