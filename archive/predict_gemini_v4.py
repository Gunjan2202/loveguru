import datetime
import streamlit as st
import google.generativeai as genai
from langgraph.graph import StateGraph
from typing import TypedDict


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
    while numerology_number > 9 and numerology_number not in [11, 22, 33]:  
        numerology_number = sum(int(digit) for digit in str(numerology_number))
    state["numerology_number"] = numerology_number
    return state

# Function to predict future based on Name, DOB, and Place of Birth
def predict_relationship_future(state: PredictionState) -> PredictionState:
    model = genai.GenerativeModel("gemini-2.0-flash-001")  # 🔥 Faster model
    prompt = (
        f"You are an expert astrologer. Based on name '{state['name']}', birth date '{state['dob']}', "
        f"place of birth '{state['place_of_birth']}', Zodiac '{state['zodiac_sign']}', "
        f"and Numerology '{state['numerology_number']}', give a **short** prediction (3-4 lines) "
        f"focusing ONLY on **love, marriage, and relationships**."
    )
    response = model.generate_content(prompt)
    state["prediction"] = response.text.strip()
    return state

# Build the LangGraph
graph = StateGraph(PredictionState)
graph.add_node("get_zodiac", get_zodiac)
graph.add_node("get_numerology", get_numerology)
graph.add_node("predict_relationship_future", predict_relationship_future)
graph.set_entry_point("get_zodiac")
graph.add_edge("get_zodiac", "get_numerology")
graph.add_edge("get_numerology", "predict_relationship_future")
graph = graph.compile()

# ========================= Streamlit UI =========================

st.set_page_config(page_title="🔮 Love & Marriage Chatbot", layout="wide")

st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
        }
        .chat-container {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            background: #1E1E1E;
            border-radius: 10px;
        }
        .chat-box {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #252525;
            color: #ffffff;
        }
        .user-msg { text-align: right; }
        .bot-msg { text-align: left; }
        .loader {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔮 Love & Marriage Chatbot")
st.markdown("**Find out what the stars say about your love life!**")

# Initialize session state for chat history and user details
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
                datetime.datetime.strptime(dob, "%d-%m-%Y")  # Validate DOB
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
                st.session_state.prediction = result["prediction"]
                st.session_state.chat_history.append({"role": "bot", "text": result["prediction"]})
                st.rerun()
            except ValueError:
                st.error("⚠️ Please enter a valid date in DD-MM-YYYY format!")

# Step 2: Show Chatbot UI (After Info is Provided)
if st.session_state.user_info:
    user_info = st.session_state.user_info
    st.markdown("### 🔮 Your Love & Marriage Prediction")

    # Chat history section
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    
    for chat in st.session_state.chat_history:
        role_class = "user-msg" if chat["role"] == "user" else "bot-msg"
        st.markdown(f'<div class="chat-box {role_class}">{chat["text"]}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # User input at bottom
    chat_input = st.text_input("💬 Ask about your love life...")
    if st.button("🔍 Ask LoveGuru"):
        if chat_input:
            model = genai.GenerativeModel("gemini-2.0-flash-001")  # 🔥 Fast response
            full_prompt = (
                f"The user {user_info['name']} was born on {user_info['dob']} in {user_info['place_of_birth']}. "
                f"Zodiac: {st.session_state.prediction}, Numerology: {st.session_state.prediction}. "
                f"Previous Chat History: {st.session_state.chat_history}. "
                f"Now answer this question: {chat_input}"
                f"Keep the answer funny as your aim is not to predict the future but to make the user laugh."
                f"Stricly keep your tone and context as Indian"
            )
            response = model.generate_content(full_prompt)
            answer = response.text.strip()

            # Save chat history
            st.session_state.chat_history.append({"role": "user", "text": chat_input})
            st.session_state.chat_history.append({"role": "bot", "text": answer})
            st.rerun()
        else:
            st.warning("⚠️ Please enter a question!")
