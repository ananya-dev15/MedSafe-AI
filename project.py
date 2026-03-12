import streamlit as st
import pandas as pd
from rapidfuzz import process
import easyocr
from PIL import Image
import numpy as np
import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="MedSafe AI",
    page_icon="🩺",
    layout="wide"
)

# -------------------------------
# CUSTOM CSS
# -------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Navbar Styling */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid #f0f0f0;
    }
    .nav-logo {
        font-size: 24px;
        font-weight: 700;
        color: #2E5BFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-links {
        display: flex;
        gap: 20px;
    }
    .nav-link {
        text-decoration: none;
        color: #666;
        font-weight: 500;
        font-size: 14px;
    }
    .nav-link.active {
        color: #2E5BFF;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #2E5BFF 0%, #172B4D 100%);
        border-radius: 16px;
        padding: 40px;
        color: white;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 15px;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    .hero-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 18px;
        opacity: 0.9;
        max-width: 600px;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        text-align: center;
    }
    .metric-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #172B4D;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
    }

    /* Feature Cards */
    .feature-card {
        border-radius: 16px;
        padding: 30px;
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    /* Container for card */
    .card-container {
        position: relative;
        height: 220px;
        z-index: 1;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: none; /* Let clicks pass through to the button behind/above */
    }

    /* Target the Streamlit Column and make it the relative parent */
    [data-testid="stColumn"] {
        position: relative !important;
        display: flex;
        flex-direction: column;
    }

    /* Target buttons and hide them but make them cover the entire column area */
    .st-key-btn_interaction, .st-key-btn_ocr, .st-key-btn_symptom, .st-key-btn_sideeffect, .st-key-btn_risk {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 100 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .st-key-btn_interaction button, .st-key-btn_ocr button, .st-key-btn_symptom button, .st-key-btn_sideeffect button, .st-key-btn_risk button {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 220px !important; /* Match card height exactly */
        opacity: 0 !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        display: block !important;
    }
    
    /* Hover Sync: Style the column's card when the column is hovered */
    [data-testid="stColumn"]:hover .feature-card {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }
    .feature-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 14px;
        opacity: 0.9;
        line-height: 1.4;
    }

    /* Gradient Variants */
    .bg-blue-cyan { background: linear-gradient(135deg, #0061ff 0%, #60efff 100%); }
    .bg-green-teal { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .bg-purple-violet { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .bg-orange-red { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); }
    .bg-navy-blue { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    /* Alternative orange-red for better contrast */
    .bg-orange-red-alt { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .bg-fire { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0 20px 0;
        font-size: 14px;
        color: #888;
        border-top: 1px solid #f0f0f0;
        margin-top: 40px;
    }

    /* Hide standard st components if needed */
    div.stButton > button {
        width: 100%;
        background-color: transparent;
        border: none;
        color: inherit;
        padding: 0;
        height: auto;
    }
    div.stButton > button:hover {
        background-color: transparent;
        color: inherit;
        border: none;
    }
    div.stButton > button:active {
        background-color: transparent;
        color: inherit;
        border: none;
    }
    div.stButton > button:focus {
        background-color: transparent;
        color: inherit;
        border: none;
        box-shadow: none;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# GENERATIVE AI HELPER
# -------------------------------

def ai_health_explanation(prompt):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a healthcare safety assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI explanation unavailable: {e}"


# -------------------------------
# LOAD DATA
# -------------------------------

@st.cache_data
def load_data():

    try:
        interactions = pd.read_csv("interactions.csv")
    except:
        interactions = pd.DataFrame(columns=["medicine1","medicine2","interaction"])

    try:
        symptoms = pd.read_csv("symptoms.csv")
    except:
        symptoms = pd.DataFrame(columns=["symptom","advice"])

    return interactions, symptoms


interactions, symptoms = load_data()

# -------------------------------
# LOAD OCR MODEL
# -------------------------------

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# -------------------------------
# SESSION STATE
# -------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"


# ====================================================
# HOME PAGE
# ====================================================

if st.session_state.page == "home":

    # Gather Metrics
    try:
        interactions_count = len(pd.read_csv("interactions.csv"))
    except:
        interactions_count = 0

    try:
        side_effects_count = len(pd.read_csv("side_effect_logs.csv"))
    except:
        side_effects_count = 0

    # Mock/Read counts for demo (usually these would be tracked properly)
    ocr_count = 0
    if os.path.exists("ocr_count.txt"):
        try:
            with open("ocr_count.txt", "r") as f:
                content = f.read().strip()
                ocr_count = int(content) if content else 42 # Fallback mock
        except:
            ocr_count = 42
    else:
        ocr_count = 42

    risk_alerts = 12 # Mock value for display

    # Top Navbar
    st.markdown("""
        <div class="nav-container">
            <div class="nav-logo">🩺 MedSafe AI</div>
            <div class="nav-links">
                <a href="#" class="nav-link active">Dashboard</a>
                <a href="#" class="nav-link">Analytics</a>
                <a href="#" class="nav-link">Reports</a>
                <a href="#" class="nav-link">Docs</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-badge">AI HEALTHCARE PLATFORM</div>
            <div class="hero-title">MedSafe AI</div>
            <div class="hero-subtitle">AI-powered medicine safety awareness platform · Powered by advanced NLP & Computer Vision</div>
        </div>
    """, unsafe_allow_html=True)

    # Platform Overview Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💊</div>
                <div class="metric-value">{interactions_count}</div>
                <div class="metric-label">Medicines Checked</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📄</div>
                <div class="metric-value">{ocr_count}</div>
                <div class="metric-label">Prescriptions Analyzed</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📋</div>
                <div class="metric-value">{side_effects_count}</div>
                <div class="metric-label">Side Effects Logged</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🚨</div>
                <div class="metric-value">{risk_alerts}</div>
                <div class="metric-label">Risk Alerts Generated</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # Core Features Section
    # In each column, the button is absolute-positioned to cover the whole column
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
            <div class="card-container">
                <div class="feature-card bg-blue-cyan">
                    <div class="feature-icon">💊</div>
                    <div class="feature-title">Medicine Interaction Checker</div>
                    <div class="feature-desc">Check potential risks between multiple medications instantly.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Interaction", key="btn_interaction"):
            st.session_state.page = "interaction"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="card-container">
                <div class="feature-card bg-green-teal">
                    <div class="feature-icon">📄</div>
                    <div class="feature-title">Prescription OCR Reader</div>
                    <div class="feature-desc">Scan and extract medicine details from prescriptions using AI.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("OCR", key="btn_ocr"):
            st.session_state.page = "ocr"
            st.rerun()

    with col3:
        st.markdown("""
            <div class="card-container">
                <div class="feature-card bg-purple-violet">
                    <div class="feature-icon">🤒</div>
                    <div class="feature-title">Symptom Guidance</div>
                    <div class="feature-desc">Get basic advice and AI insights for your health symptoms.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Symptom", key="btn_symptom"):
            st.session_state.page = "symptom"
            st.rerun()

    # Vertical spacer between rows
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    c_empty1, col4, col5, c_empty2 = st.columns([1, 2, 2, 1], gap="large")

    with col4:
        st.markdown("""
            <div class="card-container">
                <div class="feature-card bg-orange-red-alt">
                    <div class="feature-icon">📋</div>
                    <div class="feature-title">Side Effect Monitor</div>
                    <div class="feature-desc">Log and track side effects to maintain your health history.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Monitor", key="btn_sideeffect"):
            st.session_state.page = "sideeffect"
            st.rerun()

    with col5:
        st.markdown("""
            <div class="card-container">
                <div class="feature-card bg-navy-blue">
                    <div class="feature-icon">🚨</div>
                    <div class="feature-title">Emergency Risk Predictor</div>
                    <div class="feature-desc">Get critical risk analysis for emergency symptoms.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Risk", key="btn_risk"):
            st.session_state.page = "risk"
            st.rerun()

    # Footer
    st.markdown("""
        <div class="footer">
            MedSafe AI · AI-powered healthcare safety platform · Built with ❤️ for safer medicine
        </div>
    """, unsafe_allow_html=True)


# ====================================================
# MEDICINE INTERACTION
# ====================================================

elif st.session_state.page == "interaction":

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.header("💊 Medicine Interaction Checker")

    user_input = st.text_input("Enter medicines separated by comma")

    if st.button("Check Interaction"):

        meds = [m.strip().lower() for m in user_input.split(",")]

        found = False

        for i in range(len(meds)):
            for j in range(i+1, len(meds)):

                result = interactions[
                    ((interactions["medicine1"] == meds[i]) &
                     (interactions["medicine2"] == meds[j])) |

                    ((interactions["medicine1"] == meds[j]) &
                     (interactions["medicine2"] == meds[i]))
                ]

                if not result.empty:

                    st.error(f"⚠️ Interaction between {meds[i]} and {meds[j]}")
                    st.warning(result["interaction"].values[0])

                    with st.spinner("AI analyzing interaction..."):

                        ai_response = ai_health_explanation(
                            f"Explain the health risks of taking {meds[i]} and {meds[j]} together."
                        )

                    st.markdown("### 🤖 AI Medical Explanation")
                    st.write(ai_response)

                    found = True

        if not found:
            st.success("✅ No known interaction found")


# ====================================================
# OCR
# ====================================================

elif st.session_state.page == "ocr":

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.header("📄 Prescription OCR Reader")

    uploaded = st.file_uploader("Upload prescription image", type=["png","jpg","jpeg"])

    if uploaded:

        image = Image.open(uploaded)
        st.image(image)

        image_np = np.array(image)
        result = reader.readtext(image_np)

        extracted_text = []

        st.subheader("Extracted Text")

        for r in result:
            st.write(r[1])
            extracted_text.append(r[1])

        meds_db = list(set(
            interactions["medicine1"].tolist() +
            interactions["medicine2"].tolist()
        ))

        detected = []

        for word in extracted_text:

            match = process.extractOne(word.lower(), meds_db)

            if match and match[1] > 80:
                detected.append(match[0])

        if detected:

            st.success("Detected Medicines:")
            st.write(", ".join(set(detected)))

            with st.spinner("Generating AI explanation..."):

                ai_response = ai_health_explanation(
                    f"Explain the medical use and safety precautions of these medicines: {', '.join(detected)}"
                )

            st.markdown("### 🤖 AI Medicine Explanation")
            st.write(ai_response)


# ====================================================
# SYMPTOM GUIDANCE
# ====================================================

elif st.session_state.page == "symptom":

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.header("🤒 Symptom Guidance")

    symptom = st.text_input("Enter symptom")

    if st.button("Get Advice"):

        if not symptoms.empty:

            match = process.extractOne(
                symptom,
                symptoms["symptom"].tolist()
            )

            if match:

                advice = symptoms[
                    symptoms["symptom"] == match[0]
                ]["advice"].values[0]

                st.info(f"💡 Basic Advice: {advice}")

        with st.spinner("Generating AI health insight..."):

            ai_response = ai_health_explanation(
                f"A patient reports symptom '{symptom}'. Explain possible causes and give safe healthcare advice."
            )

        st.markdown("### 🤖 AI Health Insight")
        st.write(ai_response)


# ====================================================
# SIDE EFFECT MONITOR
# ====================================================

elif st.session_state.page == "sideeffect":

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.header("📋 Side Effect Monitor")

    age = st.number_input("Age", 1, 100)
    medicine = st.text_input("Medicine name")
    experience = st.text_area("Describe your experience")

    if st.button("Submit Report"):

        data = pd.DataFrame({
            "date":[datetime.datetime.now()],
            "age":[age],
            "medicine":[medicine],
            "experience":[experience]
        })

        data.to_csv("side_effect_logs.csv", mode="a", header=False, index=False)

        st.success("✅ Experience logged successfully")


# ====================================================
# EMERGENCY RISK
# ====================================================

elif st.session_state.page == "risk":

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.header("🚨 Emergency Risk Predictor")

    symptom = st.text_input("Enter symptom")

    if st.button("Check Risk"):

        symptom = symptom.lower()

        if "chest pain" in symptom:
            st.error("🚑 HIGH RISK – Visit hospital immediately")
        elif "fever" in symptom:
            st.warning("⚠️ Medium risk – Monitor condition")
        elif "headache" in symptom:
            st.info("ℹ️ Low risk – Rest and hydrate")
        else:
            st.success("Risk unclear – Monitor symptoms")

        with st.spinner("Generating AI risk analysis..."):
            ai_response = ai_health_explanation(
                f"A patient reports the symptom: '{symptom}'. Analyze potential health risks and provide safe medical safety guidance."
            )

        st.markdown("### 🤖 AI Health Insight")
        st.write(ai_response)
