import requests

url = "http://localhost:8001/stream_chat"
url_cost = "http://localhost:8001/total_cost"

headers = {"Content-type": "application/json"}


def chat(data):
    with requests.get(url, json=data, headers=headers, stream=True) as rari:
        for chunk in rari.iter_content(1024):
            print(chunk.decode("utf-8"), end="", flush=True)
    print()
    cost = requests.get(url=url_cost).json()["cost"]
    print(f"Cost for the request: {cost}$")


message = input("USER: ")
data = {"content": message}
chat(data)


message = input("USER: ")
data = {"content": message}
chat(data)

message = input("USER: ")
data = {"content": message}
chat(data)

message = input("USER: ")
data = {"content": message}
chat(data)

message = input("USER: ")
data = {"content": message}
chat(data)

message = input("USER: ")
data = {"content": message}
chat(data)
