import streamlit as st
import requests
from datetime import datetime

# Streamlit UI Configuration
st.set_page_config(
    page_title="To-Do NLP Automation Tester",
    page_icon="✅",
    layout="wide"
)

# API Configuration
FASTAPI_BASE_URL = "http://localhost:8000"

st.title("🤖 To-Do NLP Automation Tester")
st.markdown("Test the FastAPI service for task automation using text or voice input.")

# Sidebar with API status
st.sidebar.header("API Status")
try:
    health_response = requests.get(f"{FASTAPI_BASE_URL}/health", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("✅ API is online")
        health_data = health_response.json()
        st.sidebar.json(health_data)
    else:
        st.sidebar.error("❌ API is offline")
except:
    st.sidebar.error("❌ Cannot connect to API")
    st.sidebar.info("Make sure the FastAPI server is running on localhost:8000")

# Main interface
st.header("📝 Text Input Testing")

# Text input examples
example_texts = [
    "Add buy groceries tomorrow at 3pm",
    "Delete the meeting task",
    "Show me all my tasks",
    "Update the project deadline to Friday",
    "Prioritize my tasks for today",
    "What's the weather like?"
]

st.subheader("Example Inputs")
for i, example in enumerate(example_texts):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text(example)
    with col2:
        if st.button(f"Use", key=f"example_{i}"):
            st.session_state.text_input = example

# Text input box
text_input = st.text_area(
    "Enter your task-related text:",
    height=100,
    key="text_input",
    placeholder="e.g., 'Add buy groceries tomorrow at 3pm' or 'Delete the meeting task'"
)

if st.button("Process Text", type="primary"):
    if text_input.strip():
        with st.spinner("Processing text..."):
            try:
                response = requests.post(
                    f"{FASTAPI_BASE_URL}/process-text",
                    json={"text": text_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Text processed successfully!")
                    
                    # Display results in a nice format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Intent Recognition")
                        intent_color = "green" if result["intent"] != "unrelated" else "orange"
                        st.markdown(f"**Intent:** :{intent_color}[{result['intent']}]")
                        
                        if result.get("message"):
                            st.info(result["message"])
                    
                    with col2:
                        st.subheader("Extracted Information")
                        st.write(f"**Task Name:** {result.get('task_name', 'None')}")
                        st.write(f"**Task Time:** {result.get('task_time', 'None')}")
                    
                    st.subheader("Full JSON Response")
                    st.json(result)
                    
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
    else:
        st.warning("Please enter some text first.")

# Footer
st.markdown("---")
st.markdown("### 🔧 Development Notes")
st.markdown("""
**Setup Steps:**
1. Install requirements: `pip install -r requirements.txt`
2. Set your OpenRouter API key in `nlp_utils.py`
3. Run FastAPI: `uvicorn main:app --reload`
4. Run Streamlit: `streamlit run app.py`
""")