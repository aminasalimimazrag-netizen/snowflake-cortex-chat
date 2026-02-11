import streamlit as st
from snowflake.snowpark.context import get_active_session
import uuid

st.set_page_config(page_title="Cortex AI Chatbot", layout="wide")
session = get_active_session()

# SIDEBAR
with st.sidebar:
    st.title("⚙️ Settings")
    
    # ✨ Modelos base que suelen estar disponibles
    model_choice = st.selectbox(
        "Select Cortex Model:", 
        [
            "snowflake-arctic",  # Modelo propio de Snowflake
            "reka-flash",        # Alternativa ligera
            "mistral-large2"     # Versión más nueva
        ]
    )
    temp_choice = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("🤖 Cortex Chat Assistant")
st.caption("Powered by Snowflake Cortex")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    session_id = st.session_state.session_id
    clean_prompt = prompt.replace("'", "''")
    
    try:
        session.sql(f"""
            INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
            VALUES ('{session_id}', 'user', '{clean_prompt}')
        """).collect()
    except:
        pass  # Continuar aunque falle la BD
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            try:
                # Construir contexto simple
                context = f"User: {prompt}\nAssistant:"
                context_escaped = context.replace("'", "''")
                
                # ✨ Sintaxis más simple (2 parámetros)
                sql_query = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        '{model_choice}',
                        '{context_escaped}'
                    ) AS RESPONSE
                """
                
                result = session.sql(sql_query).collect()
                response_text = result[0]['RESPONSE']
                
                st.markdown(response_text)
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                clean_resp = response_text.replace("'", "''")
                
                session.sql(f"""
                    INSERT INTO DB_LAB.CHAT_APP.CONVERSATIONS (CONVERSATION_ID, ROLE, CONTENT) 
                    VALUES ('{session_id}', 'assistant', '{clean_resp}')
                """).collect()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Try selecting a different model from the sidebar")