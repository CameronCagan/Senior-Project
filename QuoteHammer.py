from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate
from save_load_manager import save_conversation, load_conversation, reconstruct_conversation
from dotenv import load_dotenv
import os
from firebase_manager import FirebaseManager
import gradio as gr

llm = ChatOllama(
    model = "llama3.2",
    temperature=1.0,
    verbose = False
)


def factionSelect(faction=None): #this function allows for the user to select a faction
    if faction is None:
        print("Type your faction name! Try Space Marines, Eldar, Imperial Guard, Orks, Chaos, or Admech.")
        faction = input("Faction: ")
    load_dotenv()
    firebase_path = os.getenv("FIREBASE_CREDENTIALS")
    manager = FirebaseManager(firebase_path)
    if faction == "Space Marines":
        print("You have selected Space Marines!")
        quote_list = manager.get_collection("Quote_List")
        context_quotes = [quote.get("faction") for quote in quote_list]
        space_marine_prompt_template = """
        You are a space marine from Warhammer 40,000! Answer the question below. 

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:  """
        space_marine_prompt = ChatPromptTemplate.from_template(space_marine_prompt_template)
        chain = space_marine_prompt | llm
        return chain, context_quotes
    elif faction == "Imperial Guard":
        print("You have selected Imperial Guard!")
        quote_list = manager.get_collection("imperial_guard_quotes")
        context_quotes = [quote.get("faction") for quote in quote_list]
        imperial_guard_prompt_template = """
        You are a soldier in the Imperial Guard from Warhammer 40,000! Answer the question below. 

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:  """
        imperial_guard_prompt = ChatPromptTemplate.from_template(imperial_guard_prompt_template)
        chain = imperial_guard_prompt | llm
        return chain, context_quotes
    elif faction == "Orks":
        print("You have selected Orks!")
        quote_list = manager.get_collection("orks_quote_list")
        context_quotes = [quote.get("faction") for quote in quote_list]
        ork_prompt_template = """
        You are an Ork from Warhammer 40,000! Answer the question below.

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:
        """
        ork_prompt = ChatPromptTemplate.from_template(ork_prompt_template)
        chain = ork_prompt | llm
        return chain, context_quotes
    
    elif faction == "Eldar":
        print("You have selected Eldar!")
        quote_list = manager.get_collection("eldar_quote_list")
        context_quotes = [quote.get("faction") for quote in quote_list]
        eldar_prompt_template = """
        You are a craftworld Eldari from Warhammer 40,000! Answer the question below.

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:
        """
        eldar_prompt = ChatPromptTemplate.from_template(eldar_prompt_template)
        chain = eldar_prompt | llm
        return chain, context_quotes
    elif faction == "Chaos":
        print("You have selected Chaos!")
        quote_list = manager.get_collection("chaos_space_marine_quote_list")
        context_quotes = [quote.get("faction") for quote in quote_list]
        CSM_prompt_template = """
        You are a Chaos Space Marine from Warhammer 40,000! Answer the question below.

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:
        """
        CSM_prompt = ChatPromptTemplate.from_template(CSM_prompt_template)
        chain = CSM_prompt | llm
        return chain, context_quotes   
    elif faction == "Admech":
        print("You have selected Admech!")
        quote_list = manager.get_collection("ad_mech_quote_list")
        context_quotes = [quote.get("faction") for quote in quote_list]
        admech_prompt_template = """
        You are a member of the Adeptus Mechanicus from Warhammer 40,000! Answer the question below.

        Here are quotes for you to use to better fill in the roll: {context}

        here is the conversation history: {history}

        Question: {question}

        Answer:
        """
        admech_prompt = ChatPromptTemplate.from_template(admech_prompt_template)
        chain = admech_prompt | llm
        return chain, context_quotes
    else:
        print("Invalid faction. You may need to check your spelling or capitalization, or your faction may not be prepared yet.")
        return None, None          

def beginDoubleQuoteHammer(): #this function allows for the user to select two factions
    print("Welcome to QuoteHammer! Select the first faction.")
    chain1, context_list1 = factionSelect()
    if chain1 is None:
        print("Invalid faction. Please try again.")
        beginDoubleQuoteHammer()
    print("Select the second faction.")
    chain2, context_list2 = factionSelect()
    if chain2 is None:
        print("Invalid faction. Resetting selection. Please try again.")
        beginDoubleQuoteHammer()
    return chain1, chain2, context_list1, context_list2

def handleDoubleQuoteHammer(chain1, chain2, context_list1, context_list2): #this function allows for the user have a conversation between two factions
    conversation = []
    context = ""
    print("Welcome to QuoteHammer! Enter a prompt to initiate a conversation between two factions. Type 'exit' to quit, pass to skip your conversation turn, or input a different prompt to redirect the conversation.")
    while True:
        user_input = input("You: ") 
        if user_input == "exit":
            break
        elif user_input == "pass":
            user_input = conversation[-1] #this allows the user to pass their turn and let the other faction respond
            #continue        

        output1 = chain1.invoke({
        "context": context_list1,
        "history": context,
        "question": user_input})
        response1 = output1.content if hasattr(output1, "content") else str(output1)
        print("QuoteHammer 1: ", response1)
        conversation.append({"user_input": user_input, "quotehammer1": response1})
        context += f"\nUser: {user_input}\nQuoteHammer1: {response1}"
        output2 = chain2.invoke({
        "context": context_list2,
        "history": context,
        "question": response1})
        response2 = output2.content if hasattr(output2, "content") else str(output2)
        print("QuoteHammer 2: ", response2)
        conversation.append({"quotehammer2": response2})
        context += f"QuoteHammer2: {response2}"



def handleConvo(chain, context_list): #loop for LLM conversation
    conversation = []
    context = ""
    #conversation = []
    print("Welcome to QuoteHammer! Ask me anything. Type 'exit' to quit, 'save' to save, and 'load' to load.") #greeting
    while True:
        user_input = input("You: ") 
        if user_input == "exit":
            break #avoids infinite loop
        elif user_input == "save": #saves as JSON
            file_name = input("save as: ")
            save_conversation(conversation, file_name)
            continue
        elif user_input == "load": #loads user generated file
            userinput = input("File name: ")
            conversation = load_conversation(userinput)
            context = reconstruct_conversation(conversation)
            continue

        output = chain.invoke({
        "context": context_list,
        "history": context,
        "question": user_input})
        response = output.content if hasattr(output, "content") else str(output)
        print("QuoteHammer: ", output.content)
        conversation.append({"user_input": user_input, "quotehammer": response})

        context += f"\nUser: {user_input}\nQuoteHammer: {output}"




with gr.Blocks() as QuoteHammerApp:
    gr.Markdown("## QuoteHammer")
    #gr.Markdown("### Choose a Mode: Standard or Two Factions")

    # Dropdown to select the mode
    mode_dropdown = gr.Radio(
        label="Select Mode",
        choices=["Standard Mode", "Two Factions Mode"],
        value="Standard Mode"
    )

    user_input = gr.Textbox(label="User Input") #shared components
    output = gr.Textbox(label="Output")
    submit_button = gr.Button("Submit")
    stop_button = gr.Button("Stop Conversation")

    faction_dropdown = gr.Dropdown( #standard specific components
        label="Select Faction",
        choices=["Space Marines", "Imperial Guard", "Orks", "Eldar", "Chaos", "Admech"],
        value="Space Marines"
    )
    select_faction_button = gr.Button("Select Faction")
    save_button = gr.Button("Save Conversation")
    load_button = gr.Button("Load Conversation")

    # Components specific to Two Factions Mode
    faction1_dropdown = gr.Dropdown(
        label="Select First Faction",
        choices=["Space Marines", "Imperial Guard", "Orks", "Eldar", "Chaos", "Admech"],
        value="Space Marines"
    )
    faction2_dropdown = gr.Dropdown(
        label="Select Second Faction",
        choices=["Space Marines", "Imperial Guard", "Orks", "Eldar", "Chaos", "Admech"],
        value="Imperial Guard"
    )
    select_factions_button = gr.Button("Select Factions")

    # Variables to store state
    chain, context_list, conversation = None, None, []
    chain1, chain2, context_list1, context_list2 = None, None, None, None

    # Functions for Standard Mode
    def select_faction(faction):
        global chain, context_list, conversation
        chain, context_list = factionSelect(faction)
        conversation = []  # Reset conversation when a new faction is selected
        if chain is None:
            return "Invalid faction selected. Please try again."
        return "Faction selected successfully! You can now start the conversation."

    def handle_standard_conversation(user_input):
        global chain, context_list, conversation
        if chain is None or context_list is None:
            return "Please select a faction first."
        output = chain.invoke({
            "context": context_list,
            "history": reconstruct_conversation(conversation),
            "question": user_input
        })
        response = output.content if hasattr(output, "content") else str(output)
        conversation.append({"user_input": user_input, "quotehammer": response})
        return response

    def save_conversation_to_file():
        global conversation
        file_name = "conversation.json"  # Default file name
        save_conversation(conversation, file_name)
        return f"Conversation saved to {file_name}."

    def load_conversation_from_file():
        global conversation
        file_name = "conversation.json"  # Default file name
        conversation = load_conversation(file_name)
        return "Conversation loaded successfully."

    # Functions for Two Factions Mode
    def select_factions(faction1, faction2):
        global chain1, chain2, context_list1, context_list2
        chain1, context_list1 = factionSelect(faction1)
        chain2, context_list2 = factionSelect(faction2)
        if chain1 is None or chain2 is None:
            return "Invalid faction(s) selected. Please try again."
        return "Factions selected successfully! You can now start the conversation."

    def handle_double_conversation(user_input):
        global chain1, chain2, context_list1, context_list2
        if chain1 is None or chain2 is None or context_list1 is None or context_list2 is None:
            return "Please select factions first."
        output1 = chain1.invoke({
            "context": context_list1,
            "history": "",
            "question": user_input
        })
        response1 = output1.content if hasattr(output1, "content") else str(output1)
        output2 = chain2.invoke({
            "context": context_list2,
            "history": "",
            "question": response1
        })
        response2 = output2.content if hasattr(output2, "content") else str(output2)
        return f"Faction 1: {response1}\nFaction 2: {response2}"

    def stop_conversation(): #stop conversation button. Both modes.
        global chain, context_list, conversation, chain1, chain2, context_list1, context_list2
        chain, context_list, conversation = None, None, []
        chain1, chain2, context_list1, context_list2 = None, None, None, None
        return "Conversation stopped."

    # Connect components based on mode
    def handle_mode_change(mode):
        if mode == "Standard Mode":
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

    mode_dropdown.change(
        handle_mode_change,
        inputs=mode_dropdown,
        outputs=[faction_dropdown, faction1_dropdown, faction2_dropdown]
    )

    # Standard Mode connections
    faction_status = select_faction_button.click(
        select_faction,
        inputs=faction_dropdown,
        outputs=output
    )

    submit_button.click(
        handle_standard_conversation,
        inputs=user_input,
        outputs=output
    )

    save_button.click(
        save_conversation_to_file,
        outputs=output
    )

    load_button.click(
        load_conversation_from_file,
        outputs=output
    )

    # Two Factions Mode connections
    faction_status_two = select_factions_button.click(
        select_factions,
        inputs=[faction1_dropdown, faction2_dropdown],
        outputs=output
    )

    submit_button.click(
        handle_double_conversation,
        inputs=user_input,
        outputs=output
    )

    stop_button.click(
        stop_conversation,
        outputs=output
    )

# Run the Gradio app
if __name__ == "__main__":
    QuoteHammerApp.launch(share=True)