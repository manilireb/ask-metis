import requests

url = "http://localhost:8001/stream_chat"
url_cost = "http://localhost:8001/total_cost"
url_insert_db = "http://localhost:8001/add_to_database"

headers = {"Content-type": "application/json"}


def chat(data):
    response = ""
    with requests.get(url, json=data, headers=headers, stream=True) as req:
        for chunk in req.iter_content(1024):
            print(chunk.decode("utf-8"), end="", flush=True)
            response += chunk.decode("utf-8")
    print()
    cost = requests.get(url=url_cost, params={"id": data["id"]}).json()["cost"]
    print(f"Cost for the request: {cost}$")
    response_data = {"content": response, "id": data["id"]}
    requests.post(url=url_insert_db, json=response_data)


message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)


message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)

message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)

message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)

message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)

message = input("USER: ")
data = {"content": message, "id": 15}
chat(data)
