import streamlit as st
from snowflake.snowpark.context import get_active_session
import uuid

# Initial page configuration
st.set_page_config(page_title="Cortex AI Chatbot", layout="wide")
session = get_active_session()

# SIDEBAR CONFIGURATION
with st.sidebar:
    st.title("⚙️ Settings")
    
    # ✨ Base models usually available in Cortex
    model_choice = st.selectbox(
        "Select Cortex Model:", 
        [
            "snowflake-arctic",  # Snowflake's native model
            "reka-flash",        # Lightweight alternative
            "mistral-large2"     # Latest version
        ]
    )
    temp_choice = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    
    # Reset conversation button
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Initialize session state for messages and session ID
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# MAIN INTERFACE
st.title("🤖 Cortex Chat Assistant")
st.caption("Powered by Snowflake Cortex")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input logic
if prompt := st.chat_input("Type your message..."):
    
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Persistence: Save user message to Snowflake table
    session_id = st.session_state.session_id
    clean_prompt = prompt.replace("'", "''") # Escape single quotes for SQL
    
    try:
        session.sql(f"""
            INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
            VALUES ('{session_id}', 'user', '{clean_prompt}')
        """).collect()
    except:
        pass  # Continue even if database insertion fails
    
    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            try:
                # Construct simple context
                context = f"User: {prompt}\nAssistant:"
                context_escaped = context.replace("'", "''")
                
                # ✨ Simplified syntax using two parameters (model and prompt)
                sql_query = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        '{model_choice}',
                        '{context_escaped}'
                    ) AS RESPONSE
                """
                
                # Execute query and extract text
                result = session.sql(sql_query).collect()
                response_text = result[0]['RESPONSE']
                
                # Display response
                st.markdown(response_text)
                
                # Update history and save assistant response to DB
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                clean_resp = response_text.replace("'", "''")
                
                session.sql(f"""
                    INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
                    VALUES ('{session_id}', 'assistant', '{clean_resp}')
                """).collect()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Try selecting a different model from the sidebar")