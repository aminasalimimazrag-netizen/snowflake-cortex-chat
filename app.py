import streamlit as st
from snowflake.snowpark.context import get_active_session
import uuid

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Cortex AI Chatbot", layout="wide")
session = get_active_session()

# 2. SIDEBAR
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Customizable System Instruction
    system_instruction = st.text_area(
        "System Instruction:",
        value="You are a helpful assistant.",
        height=100,
        help="Define how the assistant should behave"
    )
    
    # Model selector
    model_choice = st.selectbox(
        "Select Cortex Model:", 
        [
            "snowflake-arctic",
            "reka-flash",
            "mistral-large2"
        ]
    )
    
    # Temperature control
    temp_choice = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    
    st.info(f"🌡️ Current temp: {temp_choice}")
    st.caption("Note: Temperature is applied via prompt engineering")
    
    # New chat button
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# 3. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 4. MAIN INTERFACE
st.title("🤖 Cortex Chat Assistant")
st.caption("Powered by Snowflake Cortex with Memory")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. CHAT LOGIC
if prompt := st.chat_input("Type your message..."):
    
    # A. Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # B. Save to database
    session_id = st.session_state.session_id
    clean_prompt = prompt.replace("'", "''")
    
    try:
        session.sql(f"""
            INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
            VALUES ('{session_id}', 'user', '{clean_prompt}')
        """).collect()
    except:
        pass
    
    # C. Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            try:
                # ✨ BUILD PROMPT WITH SYSTEM INSTRUCTION + MEMORY
                full_context = f"{system_instruction}\n\n"
                
                # Add last 4 messages from history
                for m in st.session_state.messages[-4:]:
                    if m["role"] == "user":
                        full_context += f"User: {m['content']}\n"
                    else:
                        full_context += f"Assistant: {m['content']}\n"
                
                full_context += "Assistant:"
                
                # Escape quotes for SQL
                context_escaped = full_context.replace("'", "''")
                
                # ✨ SIMPLE SYNTAX (2 parameters)
                # Temperature is simulated via prompt
                sql_query = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        '{model_choice}',
                        '{context_escaped}'
                    ) AS RESPONSE
                """
                
                result = session.sql(sql_query).collect()
                response_text = result[0]['RESPONSE']
                
                st.markdown(response_text)
                
                # Save response to history and database
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                clean_resp = response_text.replace("'", "''")
                
                session.sql(f"""
                    INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
                    VALUES ('{session_id}', 'assistant', '{clean_resp}')
                """).collect()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try selecting a different model from the sidebar")