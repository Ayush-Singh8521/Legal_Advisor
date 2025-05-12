import streamlit as st
import requests
import json
import os
import datetime
import pandas as pd
import uuid
import time
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from apikeys import *
from legal_advisor_prompt import LEGAL_ADVISOR_PROMPT
from similar_case_prompt import SIMILAR_CASE_PROMPT
from causal_reasoning_prompt import CAUSAL_REASONING_PROMPT

# Streamlit Page Config
st.set_page_config(
    page_title="Legal Assistant - Your Friend in Legal Matters",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with user-friendly design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #2563eb;          /* Friendly blue */
        --secondary-color: #f59e0b;        /* Warm amber */
        --background-color: #fefefe;       /* Pure white */
        --card-background: #ffffff;        /* Card white */
        --text-color: #374151;             /* Warm gray text */
        --border-color: #e5e7eb;           /* Light border */
        --success-color: #22c55e;          /* Success green */
        --warning-color: #eab308;          /* Warning yellow */
        --error-color: #ef4444;            /* Error red */
        --info-color: #3b82f6;             /* Info blue */
        --font-family: 'Segoe UI', sans-serif;
        --border-radius: 12px;
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: var(--font-family);
        padding: 2rem 1rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
        font-family: var(--font-family);
        font-weight: 600;
    }
    
    /* Step-by-step wizard styling */
    .wizard-container {
        background: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--border-color);
    }
    
    .progress-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: var(--border-radius);
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }
    
    .progress-step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .progress-step-circle.active {
        background-color: var(--primary-color);
        color: white;
    }
    
    .progress-step-circle.completed {
        background-color: var(--success-color);
        color: white;
    }
    
    .progress-step-circle.inactive {
        background-color: var(--border-color);
        color: var(--text-color);
    }
    
    .progress-step-label {
        text-align: center;
        font-size: 0.9rem;
        color: var(--text-color);
    }
    
    /* Card styling */
    .welcome-card {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid var(--border-color);
    }
    
    .service-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid var(--border-color);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .service-card:hover {
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-color);
        transform: translateY(-4px);
    }
    
    .service-card.selected {
        border-color: var(--primary-color);
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }
    
    /* Service buttons container */
    .service-buttons-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
    }
    
    .service-button {
        flex: 1;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background: var(--card-background);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .service-button:hover {
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-color);
        transform: translateY(-2px);
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }
    
    .service-button-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .service-button-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .service-button-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    /* Quick questions styling */
    .quick-questions {
        background: #f8fafc;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .quick-question-button {
        display: block;
        width: 100%;
        text-align: left;
        background: var(--card-background);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-color);
        font-size: 0.95rem;
    }
    
    .quick-question-button:hover {
        background: #f0f9ff;
        border-color: var(--primary-color);
        transform: translateX(8px);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        padding: 0.75rem;
        font-size: 1rem;
        font-family: var(--font-family);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: var(--border-radius);
        padding: 0.75rem 2rem;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        font-family: var(--font-family);
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    .secondary-button {
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border: 2px solid var(--primary-color) !important;
    }
    
    .secondary-button:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Chat styling */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: var(--border-radius);
        animation: fadeInUp 0.5s ease;
    }
    
    .user-message {
        background-color: var(--primary-color);
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background-color: #f8fafc;
        color: var(--text-color);
        margin-right: 20%;
        border: 1px solid var(--border-color);
    }
    
    /* Typing animation */
    .typing-indicator {
        display: flex;
        align-items: center;
        color: var(--text-color);
        font-style: italic;
    }
    
    .typing-dots {
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    .typing-dots::after {
        content: "";
        animation: typing 1.5s infinite;
    }
    
    @keyframes typing {
        0% { content: ""; }
        25% { content: "."; }
        50% { content: ".."; }
        75% { content: "..."; }
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 3rem;
        background: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    .loading-text {
        margin-top: 1rem;
        color: var(--text-color);
        font-size: 1.1rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.8s ease;
    }
    
    /* Error and success messages */
    .custom-error {
        background-color: #fef2f2;
        color: #dc2626;
        padding: 1rem;
        border-radius: var(--border-radius);
        border: 1px solid #fecaca;
        margin: 1rem 0;
    }
    
    .custom-success {
        background-color: #f0fdf4;
        color: #16a34a;
        padding: 1rem;
        border-radius: var(--border-radius);
        border: 1px solid #bbf7d0;
        margin: 1rem 0;
    }
    
    .custom-info {
        background-color: #eff6ff;
        color: #2563eb;
        padding: 1rem;
        border-radius: var(--border-radius);
        border: 1px solid #dbeafe;
        margin: 1rem 0;
    }
    
    /* Login styling */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .progress-bar {
            flex-direction: column;
            gap: 1rem;
        }
        
        .service-card {
            padding: 1rem;
        }
        
        .service-buttons-container {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "case_corpus" not in st.session_state:
    st.session_state.case_corpus = ""
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "case_data" not in st.session_state:
    st.session_state.case_data = {}
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "service_selected" not in st.session_state:
    st.session_state.service_selected = None
if "typing_status" not in st.session_state:
    st.session_state.typing_status = False
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "quick_questions" not in st.session_state:
    st.session_state.quick_questions = []

# Helper Functions
def is_case_invalid(subject):
    """Improved case validation with partial matching"""
    invalid_cases = [
        "fight with a friend", "movie choice", "remote control", "breakup",
        "ignored by friend", "dog barking", "grocery store", "cricket argument",
        "sharing snacks", "white lie", "borrowed book", "cooking skills",
        "imaginary friend", "fictional property", "vacation promise",
        "pen stolen", "dog barking"
    ]
    subject_lower = subject.lower().strip()
    return any(invalid.lower() in subject_lower for invalid in invalid_cases)

def check_case_validity(subject):
    """Check case validity using LLM"""
    prompt = f"""
    Is this a valid legal matter for Indian courts?
    Subject: "{subject}"
    
    Answer only "VALID" or "INVALID" based on whether this is a legitimate legal issue.
    """
    try:
        response = generate_gpt_response(prompt, max_tokens=100)
        return "VALID" in response.upper()
    except:
        return True  # Default to valid if check fails

def generate_gpt_response(user_query, max_tokens=2000):
    """Generate response from GPT"""
    url = f"{OPENAI_DEPLOYMENT_ENDPOINT_GPT4}/openai/deployments/{OPENAI_DEPLOYMENT_NAME_GPT4}/chat/completions?api-version={OPENAI_API_VERSION}"
    headers = {"Content-Type": "application/json", "api-key": OPENAI_API_KEY_GPT4}
    
    # Build proper conversation context
    messages = []
    if st.session_state.chat_history:
        messages.extend(st.session_state.chat_history)
    messages.append({"role": "user", "content": user_query})
    
    data = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."
    except:
        return "I apologize for the technical difficulty. Please try again in a moment."

def generate_quick_questions(case_description):
    """Generate 5 quick questions related to the case"""
    prompt = f"""
    Based on this legal case description:
    "{case_description}"
    
    Generate 5 specific questions that the user might want to ask about their case. 
    Make each question practical and relevant to their specific situation.
    Format each question as a concise, clear question that would help them understand their rights or next steps.
    
    Return only the questions, one per line.
    """
    
    try:
        response = generate_gpt_response(prompt, max_tokens=500)
        questions = [q.strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('Based on')]
        # Clean up questions (remove numbering if present)
        clean_questions = []
        for q in questions:
            # Remove number prefixes like "1.", "1)", etc.
            cleaned = q.lstrip('0123456789.-) ').strip()
            if cleaned and not cleaned.startswith('Q'):
                clean_questions.append(cleaned)
        return clean_questions[:5]  # Return max 5 questions
    except:
        # Default questions if generation fails
        return [
            "What are my legal rights in this situation?",
            "What documents do I need to collect?",
            "How long do I have to take legal action?",
            "What are the possible outcomes of this case?",
            "Should I consult a lawyer immediately?"
        ]

def display_typing_animation():
    """Display typing animation"""
    typing_placeholder = st.empty()
    for i in range(3):
        typing_placeholder.markdown('<div class="typing-indicator">Our legal assistant is thinking<span class="typing-dots"></span></div>', unsafe_allow_html=True)
        time.sleep(1)
    typing_placeholder.empty()

def progress_bar(current_step):
    """Display progress bar for wizard"""
    steps = ["Choose Service", "Share Your Story", "Get Legal Help", "Ask Questions"]
    
    progress_html = '<div class="progress-bar">'
    for i, step in enumerate(steps, 1):
        if i < current_step:
            class_name = "completed"
        elif i == current_step:
            class_name = "active"
        else:
            class_name = "inactive"
        
        progress_html += f'''
        <div class="progress-step">
            <div class="progress-step-circle {class_name}">{i}</div>
            <div class="progress-step-label">{step}</div>
        </div>
        '''
        
        if i < len(steps):
            progress_html += '<div style="flex: 1; height: 2px; background: #e5e7eb; margin: 0 1rem;"></div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

# Login Page
if not st.session_state.is_logged_in:
    st.markdown("""
    <div class="welcome-card">
        <h1>⚖️ Legal Assistant</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">Your friendly guide through legal matters</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            st.markdown("### Welcome back!")
            email = st.text_input("Email address", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sign In", use_container_width=True):
                    if email and password:
                        st.session_state.is_logged_in = True
                        st.success("Welcome back! Let's help you with your legal matter.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please enter both email and password")
        
        with tab2:
            st.markdown("### Join our community!")
            new_email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
            new_password = st.text_input("Create password", type="password", placeholder="Create a password", key="signup_password")
            confirm_password = st.text_input("Confirm password", type="password", placeholder="Confirm your password")
            
            if st.button("Create Account", use_container_width=True):
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        st.session_state.is_logged_in = True
                        st.success("Account created successfully! Welcome!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main Application
else:
    # Header
    st.markdown("""
    <div class="welcome-card fade-in-up">
        <h1>⚖️ Welcome to Your Legal Assistant</h1>
        <p style="font-size: 1.1rem; margin-top: 1rem;">We're here to help you understand your legal situation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress_bar(st.session_state.current_step)
    
    # Step 1: Service Selection
    if st.session_state.current_step == 1:
        st.markdown('<div class="wizard-container fade-in-up">', unsafe_allow_html=True)
        st.markdown("## How can we help you today?")
        st.markdown("Choose the type of assistance you need:")
        
        # Updated service buttons with closer spacing
        st.markdown("""
        <div class="service-buttons-container">
            <div class="service-button" onclick="selectService('Legal Guidance')">
                <div class="service-button-icon">📚</div>
                <div class="service-button-title">I need legal guidance</div>
                <div class="service-button-subtitle">Get step-by-step legal advice</div>
            </div>
            <div class="service-button" onclick="selectService('Similar Cases')">
                <div class="service-button-icon">📄</div>
                <div class="service-button-title">Show me similar cases</div>
                <div class="service-button-subtitle">Find cases similar to yours</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns with closer spacing
        col1, col2 = st.columns([1, 1], gap="small")
        
        with col1:
            if st.button("📚 I need legal guidance", key="service1", help="Get step-by-step legal advice", use_container_width=True):
                st.session_state.service_selected = "Legal Guidance"
                st.session_state.current_step = 2
                st.rerun()
        
        with col2:
            if st.button("📄 Show me similar cases", key="service2", help="Find cases similar to yours", use_container_width=True):
                st.session_state.service_selected = "Similar Cases"
                st.session_state.current_step = 2
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Age verification at the bottom
        st.markdown("---")
        age = st.number_input("Before we continue, may I know your age?", min_value=1, max_value=120, step=1, help="You must be 18 or older to use this service")
        if age and age < 18:
            st.error("I'm sorry, but you must be at least 18 years old to use this legal assistance service.")
            st.stop()
    
    # Step 2: Case Details Input
    elif st.session_state.current_step == 2:
        st.markdown('<div class="wizard-container fade-in-up">', unsafe_allow_html=True)
        st.markdown(f"## Tell us about your situation")
        st.markdown(f"You've chosen: **{st.session_state.service_selected}**")
        
        with st.form("case_details"):
            st.markdown("### What happened?")
            case_subject = st.text_input(
                "Brief summary of your situation", 
                placeholder="E.g., My landlord is asking me to vacate without notice",
                help="Describe your legal issue in one line"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                case_type = st.selectbox(
                    "What type of issue is this?",
                    ["Property & Housing", "Family Matters", "Workplace Issues", 
                     "Consumer Problems", "Financial Disputes", "Other"]
                )
            
            with col2:
                incident_date = st.date_input(
                    "When did this happen?",
                    value=datetime.date.today(),
                    help="Approximate date is fine"
                )
            
            st.markdown("### Tell us more")
            case_description = st.text_area(
                "Please describe what happened in detail",
                placeholder="E.g., I am living in a rented apartment in Mumbai. My landlord suddenly asked me to vacate within 7 days without any prior notice. I have been paying rent on time and have not violated any terms of the rental agreement. I need to know my rights and what I can do in this situation.",
                height=150,
                help="Include all relevant details - dates, people involved, what was said or done"
            )
            
            # File upload (dummy implementation)
            st.markdown("### Supporting documents (optional)")
            uploaded_file = st.file_uploader(
                "Upload any relevant documents",
                type=["pdf", "jpg", "png", "docx"],
                help="Upload photos, contracts, or other documents related to your case"
            )
            if uploaded_file:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("← Go Back", type="secondary"):
                    st.session_state.current_step = 1
                    st.rerun()
            
            with col3:
                if st.form_submit_button("Get Help →", type="primary"):
                    if case_subject and case_description:
                        # Validate case
                        with st.spinner("Checking if we can help with this..."):
                            if is_case_invalid(case_subject):
                                st.error("🤔 This doesn't seem like a legal matter we can help with. Could you tell us about a different legal issue?")
                                st.info("💡 Examples of issues we can help with: property disputes, employment problems, consumer complaints, family law matters")
                            elif not check_case_validity(case_subject):
                                st.error("🤔 We couldn't understand your legal issue. Could you describe it more clearly?")
                                st.info("💡 Try to explain: What happened? Who was involved? What law or rights might be affected?")
                            else:
                                st.success("✅ We can help with this! Processing your request...")
                                st.session_state.case_data = {
                                    "subject": case_subject,
                                    "type": case_type,
                                    "date": incident_date,
                                    "description": case_description
                                }
                                st.session_state.current_step = 3
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.error("Please fill in the required fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Step 3: Legal Analysis
    elif st.session_state.current_step == 3:
        if not st.session_state.case_corpus:
            # Show loading animation
            st.markdown('<div class="loading-container">', unsafe_allow_html=True)
            st.markdown("### 🔍 Analyzing your case...")
            
            loading_messages = [
                "Reading your case details...",
                "Consulting legal databases...",
                "Preparing your personalized advice...",
                "Almost ready!"
            ]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, message in enumerate(loading_messages):
                status_text.text(message)
                progress_bar.progress((i + 1) / len(loading_messages))
                time.sleep(2)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Generate response
            case_info = f"""
            Subject: {st.session_state.case_data['subject']}
            Type: {st.session_state.case_data['type']}
            Date: {st.session_state.case_data['date']}
            Description: {st.session_state.case_data['description']}
            """
            
            if st.session_state.service_selected == "Legal Guidance":
                prompt = f"{case_info}\n{LEGAL_ADVISOR_PROMPT}"
            else:
                prompt = f"{case_info}\n{SIMILAR_CASE_PROMPT}"
            
            response = generate_gpt_response(prompt, max_tokens=3000)
            st.session_state.case_corpus = response
            st.session_state.chat_history = [
                {"role": "system", "content": "You are a legal assistant providing advice based on Indian law."},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
            
            # Generate quick questions
            st.session_state.quick_questions = generate_quick_questions(st. session_state.case_data['description'])
                                                                       
            st.rerun()
        
        # Display the legal analysis
        st.markdown('<div class="wizard-container fade-in-up">', unsafe_allow_html=True)
        st.markdown("## 📋 Your Legal Analysis")
        
        # Display case summary
        with st.expander("📝 Case Summary", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Subject:** {st.session_state.case_data['subject']}")
                st.markdown(f"**Type:** {st.session_state.case_data['type']}")
            with col2:
                st.markdown(f"**Date:** {st.session_state.case_data['date']}")
        
        # Display the analysis
        with st.container():
            st.markdown(st.session_state.case_corpus)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Continue button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Ask Questions →", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
        
        with col1:
            if st.button("← Back to Details", type="secondary", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
    
    # Step 4: Interactive Q&A
    elif st.session_state.current_step == 4:
        st.markdown('<div class="wizard-container fade-in-up">', unsafe_allow_html=True)
        st.markdown("## 💬 Ask Your Questions")
        st.markdown("Feel free to ask specific questions about your case or legal situation.")
        
        # Quick Questions Section
        if st.session_state.quick_questions:
            with st.expander("🔍 Quick Questions for Your Case", expanded=True):
                st.markdown("Click on any question to get an instant answer:")
                for question in st.session_state.quick_questions:
                    if st.button(f"❓ {question}", key=f"quick_{hash(question)}", use_container_width=True):
                        # Add question to chat
                        user_message = {"role": "user", "content": question}
                        st.session_state.chat_history.append(user_message)
                        
                        # Generate response
                        with st.spinner("Generating response..."):
                            response = generate_gpt_response(question, max_tokens=1500)
                            assistant_message = {"role": "assistant", "content": response}
                            st.session_state.chat_history.append(assistant_message)
                            st.rerun()
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            if len(st.session_state.chat_history) > 2:  # Skip system and initial messages
                for i, message in enumerate(st.session_state.chat_history[2:], 1):
                    if message["role"] == "user":
                        st.markdown(f'''
                        <div class="chat-message user-message">
                            <strong>You:</strong> {message["content"]}
                        </div>
                        ''', unsafe_allow_html=True)
                    elif message["role"] == "assistant":
                        st.markdown(f'''
                        <div class="chat-message assistant-message">
                            <strong>Legal Assistant:</strong> {message["content"]}
                        </div>
                        ''', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input(
            "Ask a question about your case:",
            placeholder="E.g., What documents do I need to gather?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        if send_button and user_input:
            # Add user message
            user_message = {"role": "user", "content": user_input}
            st.session_state.chat_history.append(user_message)
            
            # Show typing animation
            with st.spinner("Our legal assistant is thinking..."):
                time.sleep(1)  # Brief pause for better UX
                response = generate_gpt_response(user_input, max_tokens=1500)
                assistant_message = {"role": "assistant", "content": response}
                st.session_state.chat_history.append(assistant_message)
            
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Feedback section
        if not st.session_state.feedback_given and len(st.session_state.chat_history) > 4:
            st.markdown("---")
            st.markdown("### How was your experience?")
            feedback_cols = st.columns(3)
            
            with feedback_cols[0]:
                if st.button("👍 Helpful", use_container_width=True):
                    st.success("Thank you for your positive feedback!")
                    st.session_state.feedback_given = True
                    st.rerun()
            
            with feedback_cols[1]:
                if st.button("👎 Not Helpful", use_container_width=True):
                    st.info("We're sorry it wasn't helpful. Your feedback helps us improve.")
                    st.session_state.feedback_given = True
                    st.rerun()
            
            with feedback_cols[2]:
                if st.button("📝 Give Detailed Feedback", use_container_width=True):
                    with st.form("feedback_form"):
                        detailed_feedback = st.text_area("Please tell us how we can improve:")
                        if st.form_submit_button("Submit Feedback"):
                            st.success("Thank you for your detailed feedback! We'll use it to improve our service.")
                            st.session_state.feedback_given = True
                            st.rerun()
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Start Over", type="secondary", use_container_width=True):
                # Reset all session state except login
                for key in list(st.session_state.keys()):
                    if key != "is_logged_in":
                        del st.session_state[key]
                # Reinitialize necessary states
                st.session_state.user_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                st.session_state.case_corpus = ""
                st.session_state.qa_history = []
                st.session_state.case_data = {}
                st.session_state.current_step = 1
                st.session_state.service_selected = None
                st.session_state.typing_status = False
                st.session_state.feedback_given = False
                st.session_state.quick_questions = []
                st.rerun()
        
        with col2:
            if st.button("← Back to Analysis", type="secondary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        
        with col3:
            if st.button("📧 Get Summary", use_container_width=True):
                # Generate case summary
                summary_prompt = f"""
                Create a concise summary of this legal consultation session:
                
                Case: {st.session_state.case_data['subject']}
                Service: {st.session_state.service_selected}
                
                Key points discussed:
                {st.session_state.case_corpus[:500]}...
                
                Questions asked: {len(st.session_state.chat_history) // 2}
                
                Provide a brief summary of the legal advice given and next steps recommended.
                """
                
                with st.spinner("Generating summary..."):
                    summary = generate_gpt_response(summary_prompt, max_tokens=800)
                    
                st.success("Summary generated!")
                with st.expander("📄 Your Consultation Summary", expanded=True):
                    st.markdown(summary)
                    st.markdown("---")
                    st.info("💡 **Remember:** This is general legal information and not a substitute for professional legal advice from a qualified lawyer.")

# Sidebar
with st.sidebar:
    st.markdown("## 🔐 User Dashboard")
    
    if st.session_state.is_logged_in:
        st.success("✅ Logged in successfully")
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.is_logged_in = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📋 Case Overview")
    
    if st.session_state.case_data:
        st.markdown(f"**Subject:** {st.session_state.case_data.get('subject', 'N/A')}")
        st.markdown(f"**Type:** {st.session_state.case_data.get('type', 'N/A')}")
        st.markdown(f"**Service:** {st.session_state.service_selected or 'N/A'}")
        st.markdown(f"**Step:** {st.session_state.current_step} of 4")
    else:
        st.info("No case details yet")
    
    st.markdown("---")
    st.markdown("## 🆘 Need Help?")
    st.markdown("- 📞 Call: 1800-XXX-XXXX")
    st.markdown("- 📧 Email: help@legalassistant.com")
    st.markdown("- 💬 Live Chat: Available 24/7")
    
    st.markdown("---")
    st.markdown("## ⚠️ Important Notice")
    st.info("This is an AI assistant providing general legal information. For specific legal advice, consult a qualified lawyer.")
    
    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    if st.session_state.chat_history:
        st.metric("Messages", len(st.session_state.chat_history))
        st.metric("Questions Asked", len([m for m in st.session_state.chat_history if m.get("role") == "user"]))
    
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 2rem 0;">
    <p>Legal Assistant © 2025 | Your Privacy is Protected | Terms of Service | Contact Us</p>
    <p>🔒 This conversation is confidential and secure</p>
</div>
""", unsafe_allow_html=True)
                                                                        