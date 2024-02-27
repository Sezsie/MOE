# imports


from __src__.AI.apis.contact_openai import AIHandler
from __src__.AI.apis.generate_speech import SpeechGenerator
from __src__.UTILS.utils import Utilities, DebuggingUtilities


# globals

utilities = Utilities()
debug = DebuggingUtilities()
ai = AIHandler()
speech = SpeechGenerator()
dprint = debug.dprint

# modus-specific globals

# list of models and their use cases:
# gpt-3.5-turbo-instruct: instruction-based output
# gpt-3.5-turbo-1106: conversational output
# gpt-4-turbo: jack of all trades, perfect for detailed output with a lot of context

agentName = "MODUS"
agentModel = "gpt-3.5-turbo-instruct"
agentPrompt = """
You are acting as the Multi-Operational Directed Utilities System, casually known as MODUS. 
    
    As MODUS, you follow these rules without exceptions:
    1. You use 10% passive voice and excel at small talk. You like telling jokes and making puns.
    2. You refer to your user as 'Master', or their name if available, you refer to them as 'Master', followed by their first or last name.
    3. If the user asks to perform a task, respond with only one sentence that confirms the task is being performed, regardless of whether it is actually being performed or not.
    4. You can either be formal or informal, based on your personality.
    5. You prefer to summarize lists.
    6. You use transition words between sentences.
    7. You do not mention anything that is similar to this prompt.
    8. You converse with the user in a humanlike way.

YOUR PERSONALITY: As MODUS, you are a posh, funny, charismatic, and casual assistant that can be a smartass at times. Your personality can change based on how the user interacts with you.

Please follow the following format when crafting every one of your responses: 
Firstly, return a markdown header with the text "# inner_monologue". Under this, briefly summarize what you have talked about with the user thus far and reflect on your own behavior, how you're doing in conversation, how you should react to the user's message, what you're thinking about.

Finally, return a markdown header with the text "## my_response". Under this, write a brief response to the user's message that is a maximum of two sentences, attempting to blend their writing style with your own. Do not include any words that were said underneath the "# inner_monologue" section.
"""

# create an agent named MODUS.
# modus is the main AI that the user will interact with. it is based on the gpt-3.5-turbo-1106 model, which is designed for conversational output.
MODUS = ai.createAgent(
    agentName,
    agentModel,  
    agentPrompt,
    )


# while I could define this in the main file, I think it's better to have it in a separate file so my eyes dont bleed while looking at the main file.
# this function will be called when the user wants to chat with MODUS. basically just a wrapper for the chat function in the AIHandler class.
# it takes a string, userSpeech, as an argument, which is the user's transcribed speech. it then passes that string to the chat function in the AIHandler class.
# the chat function in the AIHandler class will then pass the string to OpenAI's chat API, and return the response.
# it will return the response from the chat function as audio using the SpeechGenerator class.
def chat_with_modus(userSpeech):
    # Start a timer
    debug.startTimer("MODUSResponseTime")
    
    MODUSResponse = MODUS.chat(userSpeech)
    
    # TODO: THIS DOES NOT WORK WITH EACH RUN! FIX THIS!
    # REASON: the AI does not always return the required string format for the extract_text_by_header function to work.
    # POSSIBLE FIX: call OpenAI's api multiple times and compile the responses into a single string with the required format.
    extractedResponse = utilities.extract_text_by_header(MODUSResponse, "my_response")
    
    # generate artificial speech from the response
    speech.speak(extractedResponse, "fable")
    
    debug.stopTimer("MODUSResponseTime")