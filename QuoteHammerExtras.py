from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate

llm = ChatOllama(
    model = "llama3.2",
    temperature=1.0,
    verbose = False
)

def QuoteHammer(question: str) -> str: #proof of concept of LLM being able to accept prompts
    x = llm.invoke(question)
    return x
query: str = "What is the meaning of life?" #dummy query
print(QuoteHammer(query))

def contextQuoteHammer(question: str) -> str: #Proof of Concept of LLM context being possible
    example_prompt = PromptTemplate(template = "Question: {Question}\nAnswer: {Answer}", input_variables = ["question", "answer"])
    context = [ #this provides context for how the LLM will format and answer questions
        {"Question": "What is the meaning of life?",
          "Answer": "The meaning of life is to be happy."},
        {"Question": "Who is the coolest student at DePauw University?", 
         "Answer": "The coolest student at DePauw University is Cam Cagan."},
        {"Question": "What is the best programming language?",
        "Answer": "The best programming language is Python."},
        {"Question": "What is the largest ocean on earth?", 
         "Answer": "The largest ocean on earth is the Pacific Ocean."},
        ]
    prompt = FewShotPromptTemplate(examples = context, 
                                   example_prompt= example_prompt,
                                   suffix = "Question: {input}",
                                   input_variables = ["input"]
                                    )
    runInput = prompt.format(input = question)
    response = llm.invoke(runInput)
    return response
query: str = "What are some of the most popular college majors?" #dummy query
#print(contextQuoteHammer(query))