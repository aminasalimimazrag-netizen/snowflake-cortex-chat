# Snowflake Cortex Chatbot

This project is a ChatGPT-like web application built using **Streamlit in Snowflake** and **Snowflake Cortex AI**.

## 🎯 Project Overview
- **Platform:** Streamlit in Snowflake
- **LLM Engine:** Snowflake Cortex (`cortex.complete`)
- **Storage:** Snowflake Table for chat persistence.
- **Security:** No external API keys used (100% native Snowflake).

## 🚀 Features
- Interactive chat interface with history.
- Model selection (Llama3, Mistral, etc.) and temperature slider in the sidebar.
- Automatic persistence of messages in the `CONVERSATIONS` table.
- System prompting to guide AI behavior.

## 🧱 Technical Architecture
1. **Frontend:** Streamlit (deployed inside Snowflake).
2. **AI Layer:** Snowflake Cortex functions via SQL Snowpark.
3. **Data Layer:** Snowflake database for conversation logging.

## 🧠 Validation Questions

**1. Which Cortex model did you use and why?**
I used `llama3-70b` because it is one of the most powerful models available in Cortex, providing excellent reasoning for general assistance.

**2. How do you manage the conversation history size?**
The history is managed in `st.session_state` and stored in a Snowflake table. To optimize the prompt, I only send the last few messages to the LLM to keep the context relevant.

**3. How did you build the prompt?**
The prompt is built by combining a system instruction ("You are a helpful assistant") with the user's latest message and previous context, formatted for the Cortex SQL function.

**4. What technical difficulties did you encounter?**
The main challenge was handling SQL escaping for single quotes in user messages and ensuring the JSON structure for the `cortex.complete` function was correctly formatted in SQL.

**5. How to guarantee the confidentiality of stored conversations?**
By using Snowflake's native Role-Based Access Control (RBAC), ensuring that only authorized roles can query the `CONVERSATIONS` table and keeping all data within the Snowflake security perimeter.