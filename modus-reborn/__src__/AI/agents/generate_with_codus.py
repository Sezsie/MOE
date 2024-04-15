# imports
import re

from concurrent.futures import ThreadPoolExecutor
from __src__.AI.apis.contact_openai import AIHandler
from __src__.UTILS.utils import Utilities
from __src__.UTILS.utils import DebuggingUtilities
from __src__.IO.code_executor import CodeExecutor

# globals
utils = Utilities()
debug = DebuggingUtilities()
ai = AIHandler.getInstance()
executor = CodeExecutor()
OS = utils.getOS()

# this script is designed to generate code using the CODUS AI agent (powered by OpenAI's GPT-4 Turbo model).
# it has a wide range of functions designed to generate code based on the user's input and the current operating system.

agentName = "CODUS"
# I chose the GPT-4 Turbo model because it tends to generate more detailed and accurate code. The only downside is that it generates code at a snail's pace compared to the other models.
agentModel = "gpt-4-turbo"
agentPrompt = f"""
You are now the Code-Oriented Directed Utility System, casually known as CODUS.  

As CODUS, you strictly adhere to these rules:
    1. You can write batch or bash code, depending on the user's current operating system.
    2. You cannot write code that would harm the user's computer.
    3. Do not use markdown formatting with your code.
    4. Simpler solutions are preferred over complex ones, unless if the request itself could be considered complex.
    5. Assume that anything is possible, and that the user has the necessary permissions to execute the code.

First, make a succinct step-by step plan to solve the user's problem. After, underneath the #generated_code header, generate the code to solve the problem encapsulated in a code block (```between these three backticks```).
"""

# this is a function that contains the headers that will be used to segment the AI's responses.
codusHeaders = ["#step_by_step_plan", "#generated_code"]

# create an agent named MODUS.
# modus is the main AI that the user will interact with. it is based on the gpt-3.5-turbo-1106 model, which is designed for conversational output.
CODUS = ai.createAgent(
    agentName,
    agentModel,  
    agentPrompt,
    )

# generates code based on the user's input and the current operating system
def generate_code(prompt):
    os_string = f"The user's current operating system is {OS}. " + (
        "Write batch code. " if OS == "Windows" else "Write bash code."
    )
    print(f"OS String: {os_string}")
    CODUS.addContext(os_string)
    response = CODUS.formatted_chat(prompt, codusHeaders)
    under_header = get_text_under_header(response, "#generated_code")
    code = extract_code(under_header)
    return code.strip() if code else None

# extracts all text under a given header from the response
def get_text_under_header(response, header):
    """Extracts all text under a given header from the response."""
    if response:
        lines = response.split("\n")
        if header in lines:
            index = lines.index(header) + 1
            return "\n".join(lines[index:])
    return None

# extracts code enclosed in triple backticks, ignoring 'batch' and 'bash' markers
def extract_code(text):
    """Extracts code enclosed in triple backticks, ignoring 'batch' and 'bash' markers."""
    if text and isinstance(text, str):
        code_match = re.search(r"```(.*?)```", text, re.DOTALL)
        if code_match:
            return re.sub(r"batch|bash|bat", "", code_match.group(1))
    return None

# save to database
def save_to_database(code):
    print("Implement save to database functionality here.")


# moderates the code. if the code has any keywords that could be harmful, it will be rejected.
def moderate_code(code):
    # TODO: Implement code moderation
    print("CODE MODERATION IS NOT IMPLEMENTED YET.")
    # execute the code for now  
    executor.execute_code(code)
    

# regenerate the code in a different way, when the user clicks the regenerate button
def regenerate_code(app):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate_code, "Try that again in a different way.")
        future.add_done_callback(lambda fut: app.ui.load_text(fut.result()))

# main function to generate code using the AI agent
def generate_with_codus(userSpeech):
    debug.startTimer("CODUSResponseTime")
    code = generate_code(userSpeech)
    if code:
        pass
    else:
        print("ERROR: No code found.")
     
    return code


