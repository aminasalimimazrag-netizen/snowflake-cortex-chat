# 🎯 Snowflake Cortex Chatbot Application

This repository contains a full-stack conversational AI application built entirely within the **Snowflake** ecosystem. It leverages **Streamlit in Snowflake** for the frontend and **Snowflake Cortex** for the Large Language Model (LLM) capabilities.

## 🚀 Project Overview
The objective of this project was to design a ChatGPT-like application that allows users to interact with supported LLMs directly from Snowflake, without the need for external API keys (like OpenAI) or complex infrastructure.

## 🧱 Technical Architecture
- **Frontend:** Streamlit in Snowflake.
- **AI Engine:** Snowflake Cortex (`SNOWFLAKE.CORTEX.COMPLETE`).
- **Data Layer:** Snowflake Tables (for message persistence).
- **Security:** Native Snowflake RBAC (Role-Based Access Control).

## ✨ Features
- **Interface:** Clean chat interface using `st.chat_message` and `st.chat_input`.
- **Model Selector:** Choose between `snowflake-arctic`, `reka-flash`, and `mistral-large2` in the sidebar.
- **Parameter Control:** Dynamic adjustment of the model's Temperature.
- **Persistence:** Every message (user and assistant) is automatically saved to a Snowflake table (`CONVERSATIONS`) for audit and history tracking.
- **State Management:** Uses `st.session_state` to maintain the conversation flow during the session.

## 🛠️ Environment Setup

To reproduce this project, run the following SQL script in your Snowflake worksheet:

```sql
-- Create Environment
CREATE OR REPLACE WAREHOUSE WH_LAB WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60;
CREATE OR REPLACE DATABASE DB_LAB;
CREATE OR REPLACE SCHEMA CHAT_APP;

-- Create Persistence Table
CREATE OR REPLACE TABLE DB_LAB.CHAT_APP.CONVERSATIONS (
    CONVERSATION_ID STRING,
    TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ROLE STRING,
    CONTENT STRING
);
```

🧠 Validation Questions
1. Which Cortex model did you use and why?
I implemented a selection of models including snowflake-arctic, reka-flash, and mistral-large2. I chose snowflake-arctic as the primary option because it is Snowflake s native model, optimized for enterprise tasks and efficiency within the platform.
2. How do you manage the size of the conversation history?
Currently, the history is managed through st.session_state for the immediate UI display. For the LLM context, I use a prompt construction that passes the current user input. To handle large-scale history, a "sliding window" or "message summarization" strategy could be implemented to stay within token limits.
3. How did you build the prompt?
The prompt is constructed dynamically by sanitizing the user input (escaping single quotes for SQL safety) and wrapping it in a clear context:
"User: {prompt}\nAssistant:"
This ensures the LLM understands the conversational structure.
4. What technical difficulties did you encounter?
The main challenge was handling SQL syntax requirements when inserting user-generated text into the Snowflake table. Specifically, escaping single quotes (e.g., converting "I'm" to "I''m") was crucial to prevent SQL compilation errors during the INSERT and SELECT operations.
5. How to guarantee the confidentiality of stored conversations?
Confidentiality is guaranteed by the Snowflake architecture. Since the application is native:
Data never leaves the Snowflake security perimeter.
No third-party APIs are called.
Access to the CONVERSATIONS table is restricted by Snowflake s Role-Based Access Control (RBAC).

Developed by: Amina Salimi
Context: Streamlit in Snowflake & Cortex Lab



![alt text](<images/Captura de Pantalla 2026-02-11 a las 17.17.43.png>)

![alt text](<images/Captura de Pantalla 2026-02-11 a las 16.36.37.png>)