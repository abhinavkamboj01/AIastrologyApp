

import streamlit as st
import datetime
import google.generativeai as genai

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except (FileNotFoundError, KeyError):
    st.error("Google AI API Key not found. Please create a .streamlit/secrets.toml file and add your GOOGLE_API_KEY.")
    st.stop()


MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')


# --- Simple zodiac calculation  ---
def get_zodiac_sign(day, month):
    zodiac = [
        (120, "Capricorn"), (219, "Aquarius"), (320, "Pisces"),
        (420, "Aries"), (521, "Taurus"), (621, "Gemini"),
        (722, "Cancer"), (822, "Leo"), (922, "Virgo"),
        (1022, "Libra"), (1121, "Scorpio"), (1221, "Sagittarius"), (1231, "Capricorn")
    ]
    date_val = month * 100 + day
    for cutoff, sign in zodiac:
        if date_val <= cutoff:
            return sign
    return "Capricorn"

# --- Astrology-based response  ---
def astrology_reading(name, dob, tob, place):
    zodiac = get_zodiac_sign(dob.day, dob.month)
    personality_traits = {
        "Aries": "Energetic, bold, and ambitious.",
        "Taurus": "Stable, reliable, and loves comfort.",
        "Gemini": "Curious, adaptable, and expressive.",
        "Cancer": "Emotional, nurturing, and intuitive.",
        "Leo": "Confident, creative, and loves attention.",
        "Virgo": "Analytical, detail-oriented, and practical.",
        "Libra": "Balanced, social, and values harmony.",
        "Scorpio": "Passionate, determined, and mysterious.",
        "Sagittarius": "Adventurous, optimistic, and freedom-loving.",
        "Capricorn": "Disciplined, responsible, and ambitious.",
        "Aquarius": "Innovative, independent, and humanitarian.",
        "Pisces": "Compassionate, artistic, and dreamy."
    }
    reading = f"""
    Hello **{name}**,  
    Based on your birth date, your zodiac sign is **{zodiac}**.  
    *Traits: {personality_traits.get(zodiac, "Unique and special personality.")}* Your birth time ({tob}) and place ({place}) suggest a unique destiny, deeply connected to the cosmos.
    """
    return reading, zodiac


def ai_response(question, zodiac, name):
    
    prompt = f"""
    You are a wise and compassionate AI Astrologer. You provide insightful and positive guidance based on the stars.
    The user is {name}, whose zodiac sign is {zodiac}.
    Answer their astrology question with warmth, wisdom, and a touch of cosmic magic.

    Question: "{question}"
    Answer:
    """
    try:
        # Define generation parameters
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "max_output_tokens": 300,
        }
        
        # Calling the Gemini API
        response = MODEL.generate_content(prompt, generation_config=generation_config)
        
        
        answer = response.text.strip()
        
        if not answer:
            answer = " The stars are quiet right now, but trust that guidance will come to you soon."
        return answer
    except Exception as e:
        
        st.error(f"An error occurred while consulting the stars. The cosmic energies might be disrupted. Please try again later.")
        st.error(f"Details: {e}") 
        return "Sorry, I couldn't connect to the celestial realm. Please try again."


# --- Streamlit UI  ---
st.set_page_config(page_title="AI Astrologer")

st.title("AI Astrologer App")
st.write("Enter your birth details and ask the stars for guidance.")

# Initialize session state variables
if "reading_generated" not in st.session_state:
    st.session_state.reading_generated = False
    st.session_state.reading = ""
    st.session_state.zodiac = ""
    st.session_state.name = ""
    st.session_state.diary = []

# Collect inputs
with st.form("birth_details_form"):
    name = st.text_input("Name")
    dob = st.date_input("Date of Birth", datetime.date(2000, 1, 1))
    tob = st.time_input("Time of Birth", datetime.time(12, 0))
    place = st.text_input("Place of Birth")
    submitted = st.form_submit_button("Get Astrology Reading")

if submitted:
    if name and dob and tob and place:
        reading, zodiac = astrology_reading(name, dob, tob, place)
        st.session_state.reading_generated = True
        st.session_state.reading = reading
        st.session_state.zodiac = zodiac
        st.session_state.name = name
    else:
        st.warning(" Please fill in all the details.")

if st.session_state.reading_generated:
    st.markdown("---")
    st.markdown(st.session_state.reading)

    st.subheader("Ask a Question to the Stars ")
    question = st.text_input("Your Question:", key="question_input")

    if st.button("Ask the Stars"):
        if question:
            with st.spinner("Consulting the cosmos... "):
                response = ai_response(question, st.session_state.zodiac, st.session_state.name)
            
            st.markdown(response)

            st.session_state.diary.append(
                {"question": question, "answer": response, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
            )
        else:
            st.warning(" Please type your question before asking.")

# Display diary
if st.session_state.diary:
    st.markdown("---")
    st.subheader("📖 Your Astrology Diary")
    for entry in reversed(st.session_state.diary):
        st.markdown(f"**{entry['time']}** — *You asked:* {entry['question']}")
        st.markdown(f"> **Astrologer’s Answer:** {entry['answer']}")
        st.markdown("---")