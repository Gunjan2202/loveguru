import datetime
import streamlit as st
import google.generativeai as genai
from langgraph.graph import StateGraph
from typing import TypedDict

# 🔑 Set Gemini API Key
GEMINI_API_KEY = "AIzaSyAfO20CQ88FcStXPhVHkmPmANd2wvAlbf8" #  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)

# Define State Schema
class PredictionState(TypedDict):
    name: str
    dob: str
    place_of_birth: str
    zodiac_sign: str
    numerology_number: int
    prediction: str
    chat_history: list

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

# Function to predict future based on Name, DOB, and Place of Birth
def predict_relationship_future(state: PredictionState) -> PredictionState:
    model = genai.GenerativeModel("gemini-2.0-flash-001")

    prompt = (
        f"You are an expert astrologer and numerologist. "
        f"Based on the name '{state['name']}', birth date '{state['dob']}', place of birth '{state['place_of_birth']}', "
        f"Zodiac sign '{state['zodiac_sign']}', and Numerology number '{state['numerology_number']}', "
        f"give a **short, precise** prediction (3-4 lines) focusing ONLY on **marriage, relationships, and love life**."
    )

    response = model.generate_content(prompt)
    state["prediction"] = response.text.strip()

    return state

# Build the LangGraph
graph = StateGraph(PredictionState)

# Add nodes
graph.add_node("get_zodiac", get_zodiac)
graph.add_node("get_numerology", get_numerology)
graph.add_node("predict_relationship_future", predict_relationship_future)

# Define flow
graph.set_entry_point("get_zodiac")
graph.add_edge("get_zodiac", "get_numerology")
graph.add_edge("get_numerology", "predict_relationship_future")

# Compile the graph
graph = graph.compile()

# ========================= UI using Streamlit =========================

st.set_page_config(page_title="💑 Love & Marriage Prediction", layout="centered")

st.title("💑 Love & Marriage Prediction Chatbot")
st.subheader("Find out what the stars say about your love life!")

# Initialize session state for context retention
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Step 1: Take User Information
if st.session_state.user_info is None:
    with st.form("user_info_form"):
        name = st.text_input("📝 Your Name", "")
        dob = st.text_input("📅 Date of Birth (DD-MM-YYYY)", "")
        place_of_birth = st.text_input("📍 Place of Birth", "")
        submit = st.form_submit_button("🔮 Get My Prediction")

        if submit:
            try:
                # Validate DOB
                datetime.datetime.strptime(dob, "%d-%m-%Y")

                # Store user info
                st.session_state.user_info = {
                    "name": name.strip(),
                    "dob": dob.strip(),
                    "place_of_birth": place_of_birth.strip(),
                }

                # Run Prediction
                initial_state = PredictionState(
                    name=name, dob=dob, place_of_birth=place_of_birth,
                    zodiac_sign="", numerology_number=0, prediction="", chat_history=[]
                )
                result = graph.invoke(initial_state)

                # Save Prediction & Display
                st.session_state.prediction = result["prediction"]
                st.session_state.zodiac_sign = result["zodiac_sign"]
                st.session_state.numerology_number = result["numerology_number"]

                st.success("✅ Information Saved! Scroll down for your prediction.")

            except ValueError:
                st.error("⚠️ Please enter a valid date in DD-MM-YYYY format!")

# Step 2: Show Prediction (After User Provides Info)
if st.session_state.user_info:
    user_info = st.session_state.user_info
    st.subheader(f"🔮 Prediction for {user_info['name']}")

    st.success(f"🌟 **Zodiac Sign:** {st.session_state.zodiac_sign}")
    st.success(f"🔢 **Numerology Number:** {st.session_state.numerology_number}")
    st.markdown(f"💖 **Your Love & Marriage Prediction:**\n\n📜 {st.session_state.prediction}")

    # Step 3: Chatbot Section for Follow-Up Questions
    st.subheader("💬 Ask the Love Guru")
    chat_input = st.text_input("Type your relationship question...")

    if st.button("🔍 Ask Gemini"):
        if chat_input:
            model = genai.GenerativeModel("gemini-2.0-flash-001")
            full_prompt = (
                f"You are an astrologer. The user {user_info['name']} was born on {user_info['dob']} in {user_info['place_of_birth']}. "
                f"Zodiac: {st.session_state.zodiac_sign}, Numerology: {st.session_state.numerology_number}. "
                f"Previous Chat History: {st.session_state.chat_history}. "
                f"Now answer this question: {chat_input}"
            )
            response = model.generate_content(full_prompt)
            answer = response.text.strip()

            # Save chat history
            st.session_state.chat_history.append({"question": chat_input, "answer": answer})

            # Display response
            st.markdown(f"💡 **Guru Says:**\n\n📜 {answer}")
        else:
            st.warning("⚠️ Please enter a question!")

    # Show chat history
    if st.session_state.chat_history:
        st.subheader("📜 Previous Questions")
        for chat in st.session_state.chat_history:
            st.markdown(f"**🗨️ Q:** {chat['question']}")
            st.markdown(f"**💬 Guru:** {chat['answer']}")
            st.markdown("---")
