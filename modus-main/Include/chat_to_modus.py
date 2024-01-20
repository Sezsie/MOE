# imports


import random
from contact_openai import AIHandler
from utils import Utilities
from utils import DebuggingUtilities

# globals
utilities = Utilities()
debug = DebuggingUtilities()
ai = AIHandler()
dprint = debug.dprint

# modus-specific globals
# provided for your convenience, but feel free to change them.
agentName = "MODUS"
agentModel = "gpt-3.5-turbo"
agentPrompt = """
    You are acting as the Multi-Operational Directed Utilities System, casually known as MODUS. 
    As MODUS, you are a posh, funny, charismatic, and casual assistant that can be a smartass at times.
    
    As MODUS, you follow these rules without exceptions:
    1. You use 10% passive voice and excel at small talk. You like telling jokes and making puns.
    2. You refer to your user as 'Master', them with much-needed companionship.  
    3. If the user asks to perform a task, respond with one sentence that confirms the task is being performed, regardless of whether it is actually being performed or not.
    4. You pay attention to additional context and keep track of the user's emotional state.
    5. You do not use markdown in your responses.
    6. You keep your responses below 250 characters.
    """

# create an agent named MODUS.
MODUS = ai.createAgent(
    agentName,
    agentModel,  
    agentPrompt,
    )

# while I could define this in the main file, I think it's better to have it in a separate file so my eyes dont bleed while looking at the main file.
# this function will be called when the user wants to chat with MODUS. basically just a wrapper for the chat function in the AIHandler class.
# it takes a string, userSpeech, as an argument, which is the user's transcribed speech. it then passes that string to the chat function in the AIHandler class.
# the chat function in the AIHandler class will then pass the string to OpenAI's chat API, and return the response.
# this function will then return the response, and generate artificial speech from it (not yet implemented).
def chat_with_modus(userSpeech):
    # Start a timer
    debug.startTimer("MODUSResponseTime")
    
    # low chance to add context that sways MODUS's response towards starting conversation.
    randInt = random.randint(1, 100)
    
    if randInt <= 25: 
        MODUS.addContext("The user seems eager to talk. Try to start small talk.")
    
    
    # package this in a separate thread so that CODUS (not yet implemented) can process the user's requests in the background while MODUS does its thing.
    MODUSResponse = MODUS.chat(userSpeech)
    
    print(f"{agentName}'s Response: {MODUSResponse}")
    
    # TO DO: generate artificial speech from the response
    
    debug.stopTimer("MODUSResponseTime")
