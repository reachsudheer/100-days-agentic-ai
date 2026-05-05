import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Personal Email Assistant - Day 001", page_icon="📧")

st.title("📧 Personal Email Assistant — Day 001")
st.caption("Powered by Gmail API + LangChain + GPT-4o-mini")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📬 Read & Classify Inbox", use_container_width=True):
        with st.spinner("Reading and classifying your inbox…"):
            result = run_agent(
                "Fetch my 10 most recent emails and classify each one as "
                "Work, Personal, Newsletter, Urgent, or Spam."
            )
        st.subheader("Inbox Classification")
        st.write(result)

with col2:
    if st.button("✅ Extract Action Items", use_container_width=True):
        with st.spinner("Extracting action items from your inbox…"):
            result = run_agent(
                "Read my 10 most recent emails and extract all action items "
                "or tasks that need follow-up. Return a bullet-point list."
            )
        st.subheader("Action Items")
        st.write(result)

with col3:
    if st.button("✍️ Draft Replies", use_container_width=True):
        with st.spinner("Drafting replies for emails that need a response…"):
            result = run_agent(
                "Read my 5 most recent emails. For any email that appears to need "
                "a reply (not newsletters or automated notifications), draft a brief "
                "professional reply."
            )
        st.subheader("Draft Replies")
        st.write(result)

st.divider()

st.subheader("💬 Ask your assistant anything about your email")
user_query = st.text_input(
    "",
    placeholder="e.g. 'Do I have any emails from my boss?' or 'Summarize urgent emails'",
)

if st.button("Ask", use_container_width=False) and user_query.strip():
    with st.spinner("Thinking…"):
        result = run_agent(user_query)
    st.markdown("**Assistant:**")
    st.write(result)
