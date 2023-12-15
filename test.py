from model import ChatModel

chat_model = ChatModel()
query = input(
    "On-Demand-GPT4: Hi, I'm GPT4 with an on-demand payment. I provide information about the cost after each request.\nHow can I help you? \nUSER: "
)
while query != "q":
    answer, info = chat_model.chat(query)
    print(f"On-Demand-GPT4: {answer}")
    print(f"{info}$")
    query = input("USER: ")
