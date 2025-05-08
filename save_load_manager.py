import json
import os

def save_conversation(conversation, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=4)
    print(f"Conversation saved to {filename}")

def load_conversation(filename):
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        conversation = json.load(f)
    print(f"Conversation loaded from {filename}")
    return conversation

def reconstruct_conversation(context_data):
    context = ""
    for round in context_data:
        context += f"\nUser: {round['user_input']}\nQuoteHammer: {round['quotehammer']}"
    return context