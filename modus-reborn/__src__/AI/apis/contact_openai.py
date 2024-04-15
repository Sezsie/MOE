

import openai
from __src__.UTILS.utils import Utilities, DebuggingUtilities

utils = Utilities()
debug = DebuggingUtilities()
dprint = debug.dprint

api_key = Utilities.getOpenAIKey()

# a class that handles all the agents that are created. this class is a singleton, so only one instance of it can exist at a time.
# the basic concept is that the AIHandler manages all the agents that are created, and the agents themselves manage their own message logs and responses.
# TODO(?): consider adding a merge function that combines the message logs of two agents, so that an agent can have context from another agent's interactions.

class AIHandler:
    _instance = None

    @staticmethod 
    def getInstance():
        if AIHandler._instance is None:
            AIHandler()
        return AIHandler._instance

    def __init__(self):
        if AIHandler._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            openai.api_key = api_key
            self.client = openai
            self.agents = {}
            AIHandler._instance = self
    
    # create an agent with the given name, model, and system prompt. the agent remembers its name and previous messages.
    def createAgent(self, agentname, agentmodel, systemprompt):
        self.agents[agentname] = Agent(agentname, agentmodel, systemprompt, self.client)
        return self.agents[agentname] 
    
    def getAgent(self, agentname):
        if agentname in self.agents:
            return self.agents[agentname]
        else:
            return None
    
    # remove an agent from the list of agents
    def deleteAgent(self, agentname):
        if agentname in self.agents:
            del self.agents[agentname]
        else:
            return None
        
    # get the message history of a particular agent
    def getAgentHistory(self, agentname):
        if agentname in self.agents:
            return self.agents[agentname].message_logs
        else:
            return None
     
    # get the list of all agents   
    def getAllAgents(self):
        return self.agents
    
    # get all agents, then print their names and message histories. this is to check that there is no memory overlap between agents.
    def getAllAgentsHistory(self):
        agents = self.getAllAgents()
        for agent in agents:
            print(agent)
            print(self.getAgentHistory(agent))
    
    
    
# TODO: consider swapping from OpenAI's platform to Mistral's platform, as the pricing is more reasonable and there is more model variety.  
class Agent:
            
    def __init__(self, agentname, inputmodel, systemprompt, newClient):
        systemprompt = "Your name is " + agentname + ". " + systemprompt
        
        self.ai_handler = AIHandler.getInstance()
        self.message_logs = [{"role": "system", "content": systemprompt}]
        self.model = inputmodel
        self.client = newClient
        self.agentname = agentname
    
    # so openai has a limit on how many tokens it can use as context. this function checks if the message logs have too many characters.
    # if the message logs strings have too many tokens, it will remove the oldest non-system messages until the message logs have less than a max amount of characters.
    def check_message_logs(self):
        
        # every token is equal to 5 characters, roundabout, so we will use that as a basis for the max amount of tokens.
        # the max amount of tokens for gpt-3.5-turbo is 2048 or so, so we will use 2000 as the max amount of tokens to be safe.
        # we multiply the max amount of tokens by 5 to convert to the max amount of characters, which is easier to check.
        max_tokens = 4000 * 5 # about 20000 characters

        # get the message logs
        message_logs = self.message_logs
        
        # get the total amount of tokens in the message logs
        total_tokens = 0
        for message in message_logs:
            total_tokens += len(message["content"].split(" "))
        
        # if the total amount of tokens is greater than the max amount of tokens, remove the oldest non-system messages until the total amount of tokens is less than the max amount of tokens.
        while total_tokens > max_tokens:
            for message in message_logs:
                if message["role"] != "system":
                    print(f"Removing message from {message['role']}: {message['content']}")
                    message_logs.remove(message)
                    total_tokens -= len(message["content"].split(" "))
                    break
        
        # set the message logs to the new message logs
        self.message_logs = message_logs
        
   
    def chat(self, message):
        self.check_message_logs()
        debug.startTimer("OpenAIChat" + self.agentname)

        self.message_logs.append({"role": "user", "content": "User's Message: " + message})

        if self.model == "gpt-3.5-turbo-instruct":
            agentResponse = self.legacy_chat()
        else:
            response = self.client.chat.completions.create(
                model=self.model or "gpt-3.5-turbo",
                messages=self.message_logs
            )
            agentResponse = response.choices[0].message.content

        debug.stopTimer("OpenAIChat" + self.agentname)

        self.message_logs.append({"role": "assistant", "content": agentResponse})
        return agentResponse

    def legacy_chat(self):
        
        # generating the prompt for the legacy chat completion
        prompt = "\n".join([msg["content"] for msg in self.message_logs])
        
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=2048 
        )
        
        # extracting the response and usage information
        agentResponse = response.choices[0].text

        return agentResponse
    
    # this method is used to steer the AI's responses based on the context of the headers.
    # NOTE: IN ORDER FOR THIS TO WORK, THE AI'S PROMPT MUST HAVE DESCRIPTIONS OF THE HEADERS IN THE PROMPT.
    def formatted_chat(self, userText, headers):
        
        totalString = ""
        for index, header in enumerate(headers):
            # add context to direct the AI's responses
            self.addContext(header)
            
            # generate and append the response
            response = self.chat(userText)
            
            totalString += f"{header}\n" + response + "\n"
        
        return totalString
    
    # add a one-shot context to the AI's responses.
    def addContext(self, message):
        dprint(f"Context Added: {message}") 
        self.message_logs.append({"role": "system", "content": "Context: " + message})
    
    # deletes all currently stored system messages, except for the first one (the first one is what sets the AI's personality and rules.)
    def wipeSystemMessages(self):
        self.message_logs = self.message_logs[:1]
        
    # sometimes neccessary to reinforce format
    def addAssistantMessage(self, message):
        self.message_logs.append({"role": "assistant", "content": message})
        

if __name__ == "__main__":
    # get the MODUS agent
    ai = AIHandler()
    MODUS = ai.getAgent("MODUS")
    # if the agent does not exist print an error message
    if MODUS is None:
        print("MODUS agent does not exist.")
    else:
        print("MODUS agent found.")
