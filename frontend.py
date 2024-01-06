from collections import deque

import requests
import streamlit as st

chat_url = "http://localhost:8001/stream_chat"
url_cost = "http://localhost:8001/total_cost"
url_insert_db = "http://localhost:8001/add_to_database"
url_create_new_session = "http://localhost:8001/create_new_session"
url_get_session_thumbnails = "http://localhost:8001/get_session_thumbnails"
url_load_existing_session = "http://localhost:8001/load_existing_session"
url_delete_session = "http://localhost:8001/delete_session"
url_get_current_model_name = "http://localhost:8001/get_current_model_name"

headers = {"Content-type": "application/json"}

st.set_page_config(page_title="\U0001F916 On-Demand GPT")


def load_thumbnails():
    thumbnails = requests.get(url=url_get_session_thumbnails).json()
    st.session_state.session_thumbnails = deque(
        set(zip(thumbnails["ids"], thumbnails["texts"]))
    )


def get_new_session():
    id = requests.get(url=url_create_new_session).json()["id"]
    st.session_state.id = id
    st.session_state.messages = []


# Initial load
if "id" not in st.session_state.keys():
    get_new_session()
    load_thumbnails()


if prompt := st.chat_input(placeholder="Message ChatGPT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Cache first message in thumbnails
if len(st.session_state.messages) == 1:
    st.session_state.session_thumbnails.appendleft((st.session_state.id, prompt))

deleted_session = None

with st.sidebar:
    if st.button("New Chat", key="new_chat", use_container_width=True):
        get_new_session()

    for thumbnail in st.session_state.session_thumbnails:
        thumbnail_text = thumbnail[1]
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            if st.button(
                thumbnail_text,
                key=thumbnail[0],
                use_container_width=True,
            ):
                id = thumbnail[0]
                if id != st.session_state.id:
                    history = requests.get(
                        url=url_load_existing_session, params={"id": id}
                    ).json()["chat_history"]
                    st.session_state.messages = []
                    for msg in history:
                        st.session_state.messages.append(
                            {
                                "role": "user"
                                if msg["message_type"] == "Human"
                                else "assistant",
                                "content": msg["message_text"],
                            }
                        )
                    st.session_state.id = id
            with col2:
                if st.button("X", key=-thumbnail[0]):
                    requests.post(url=url_delete_session, params={"id": thumbnail[0]})
                    deleted_session = (thumbnail[0], thumbnail[1])

if deleted_session:
    st.session_state.session_thumbnails.remove(deleted_session)
    get_new_session()
    st.rerun()

    # load messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)


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
        current_model = requests.get(
            url=url_get_current_model_name, params={"id": data["id"]}
        ).json()["model_name"]
        info_string = f"""
        <div style="color:blue; text-align: right;"> **{current_model}** </div>
        <div style="color:green; text-align: right;"> **{cost:.4f}$** </div>
        """
        placeholder.markdown(response + info_string, unsafe_allow_html=True)
        response_data = {
            "content": response + info_string,
            "id": data["id"],
        }
        # write response back to data base
        requests.post(url=url_insert_db, json=response_data)

    # add response message to session state
    message = {"role": "assistant", "content": response + info_string}
    st.session_state.messages.append(message)
