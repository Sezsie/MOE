# imports

from __src__.AI.apis.contact_openai import AIHandler
from __src__.UTILS.utils import Utilities
from __src__.UTILS.utils import DebuggingUtilities

# globals

utilities = Utilities()
debug = DebuggingUtilities()
ai = AIHandler()
OS = utilities.getOS()
dprint = debug.dprint

# modus-specific globals
# provided for your convenience, but feel free to change them.

# list of models and their use cases:
# gpt-3.5-turbo-instruct: instruction-based output
# gpt-3.5-turbo-1106: conversational output
# gpt-4-turbo: jack of all trades, perfect for detailed output with a lot of context.

agentName = "CODUS"
agentModel = "gpt-4-turbo-preview"
agentPrompt = f"""
You are now the Code-Oriented Directed Utility System, casually known as CODUS. The user's current operating system is {OS}.

As CODUS, you strictly adhere to these rules:
    1. You only write batch or bash code, depending on the user's current operating system.
    2. If the user is on Windows, you write batch code and assume the user also has nircmd installed.
    3. If the user is on Linux, you write bash code.
    4. You cannot write code that would harm the user's computer.
    
As CODUS, you also follow this format when crafting every one of your responses:
    1. Firstly, return a markdown header with the text "# inner_monologue". Under this, come up with a succinct plan to generate code that satisfies the user's request. 
    2. Finally, return a markdown header with the text "## generated_code". Under this, write appropriate code that satisfies the user's request in plain text.
 
In summary, you must generate code that satisfies the user's request. You must also follow the format above when crafting your responses.   
"""

# create an agent named MODUS.
# modus is the main AI that the user will interact with. it is based on the gpt-3.5-turbo-1106 model, which is designed for conversational output.
CODUS = ai.createAgent(
    agentName,
    agentModel,  
    agentPrompt,
    )

def generate_with_codus(userSpeech):
    # Start a timer
    debug.startTimer("CODUSResponseTime")
    
    CODUSResponse = CODUS.chat(userSpeech)
    
    extractedResponse = utilities.extract_text_by_header(CODUSResponse, "generated_code")
    print(extractedResponse)
    
    debug.stopTimer("CODUSResponseTime")