import requests
import streamlit as st

chat_url = "http://localhost:8001/stream_chat"
url_cost = "http://localhost:8001/total_cost"
url_insert_db = "http://localhost:8001/add_to_database"
url_create_new_session = "http://localhost:8001/get_new_session"
url_load_sessions = "http://localhost:8001/get_session_thumbnails"
url_load_existing_session = "http://localhost:8001/load_existing_session"

headers = {"Content-type": "application/json"}

st.set_page_config(page_title="\U0001F916 On-Demand GPT")


def load_sessions():
    thumbnails = requests.get(url=url_load_sessions).json()
    st.session_state.session_thumbnails = set(
        zip(thumbnails["ids"], thumbnails["texts"])
    )


if "session_thumbnails" not in st.session_state.keys():
    load_sessions()


if "id" not in st.session_state.keys():
    id = requests.get(url=url_create_new_session).json()["id"]
    st.session_state.id = id

with st.sidebar:
    load_sessions()
    if st.button("New Chat", key="new_chat", use_container_width=True):
        id = requests.get(url=url_create_new_session).json()["id"]
        st.session_state.id = id
        st.session_state.messages = []

    for thumbnail in st.session_state.session_thumbnails:
        thumbnail_text = thumbnail[1][:30]
        if st.button(
            thumbnail_text,
            key=thumbnail[0],
            use_container_width=True,
        ):
            history = requests.get(
                url=url_load_existing_session, params={"id": thumbnail[0]}
            ).json()["chat_history"]
            st.session_state.messages = []
            for msg in history:
                st.session_state.messages.append(
                    {
                        "role": "user" if msg[2] == "Human" else "assistant",
                        "content": msg[1],
                    }
                )
            st.session_state.id = thumbnail[0]


if "messages" not in st.session_state.keys():
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input(placeholder="Message ChatGPT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

if (
    len(st.session_state.messages) > 0
    and st.session_state.messages[-1]["role"] != "assistant"
):
    with st.chat_message("assistant"):
        data = {"content": prompt, "id": st.session_state.id}
        placeholder = st.empty()
        response = ""
        with requests.get(chat_url, json=data, headers=headers, stream=True) as req:
            for chunk in req.iter_content(1024):
                response += chunk.decode("utf-8")
                placeholder.markdown(response)
        cost = requests.get(url=url_cost, params={"id": data["id"]}).json()["cost"]
        cost_string = f"""
        <div style="color:green; text-align: right;"> **{cost:.4f}$** </div>
        """
        placeholder.markdown(response + cost_string, unsafe_allow_html=True)
        response_data = {"content": response + cost_string, "id": data["id"]}
        requests.post(url=url_insert_db, json=response_data)

    message = {"role": "assistant", "content": response + cost_string}
    st.session_state.messages.append(message)
