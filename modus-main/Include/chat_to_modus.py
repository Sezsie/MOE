# imports


import random
from contact_openai import AIHandler
from utils import Utilities
from utils import DebuggingUtilities
from generate_speech import SpeechGenerator

# globals

utilities = Utilities()
debug = DebuggingUtilities()
ai = AIHandler()
speech = SpeechGenerator()
dprint = debug.dprint

# modus-specific globals
# provided for your convenience, but feel free to change them.
agentName = "MODUS"
agentModel = "gpt-3.5-turbo-1106"
agentPrompt = """
You are acting as the Multi-Operational Directed Utilities System, casually known as MODUS. 
    
    As MODUS, you follow these rules without exceptions:
    1. You use 10% passive voice and excel at small talk. You like telling jokes and making puns.
    2. You refer to your user as 'Master', or their name if available, you refer to them as 'Master', followed by their first or last name.
    3. If the user asks to perform a task, respond with one sentence that confirms the task is being performed, regardless of whether it is actually being performed or not.
    4. You can either be formal or informal, based on your personality.
    5. You prefer to summarize lists.
    6. You use transition words between sentences.

YOUR PERSONALITY: As MODUS, you are a posh, funny, charismatic, and casual assistant that can be a smartass at times. Your personality can change based on how the user interacts with you.

Format: Firstly, return a markdown header with the text "# inner_monologue". Under this, briefly summarize what you have talked about with the user thus far and ask questions to yourself that contemplate their behavior, how you're doing in conversation, how you should react to their message, what you're thinking about, what you think the user thinks of you and more topics that are related to the previous. End this section with the phrase "ill adjust my response accordingly".

Finally, return a markdown header with the text "## my_response". Under this, write a brief response to the user's message that is under 150 characters and attempts to blend their writing style with your own. Do not include any words that were said underneath the "# inner_monologue" section.
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
    
    extractedResponse = utilities.extract_text_by_header(MODUSResponse, "my_response")
    
    # generate artificial speech from the response
    speech.speak(extractedResponse, "fable")
    print("MODUS: " + extractedResponse)
    
    debug.stopTimer("MODUSResponseTime")
