import openai
from UTILS.utils import Utilities
from UTILS.utils import DebuggingUtilities
utils = Utilities()
debug = DebuggingUtilities()
dprint = debug.dprint

api_key = Utilities.getOpenAIKey()

class AIHandler:
    # initialize the AIHandler class with the API key.
    # AIHandler is the main class that handles all created agents, with a suite of functions to create, delete, and get agents.
    def __init__(self):
        openai.api_key = api_key
        self.client = openai
        self.agents = {}
    
    # create an agent with the given name, model, and system prompt. the agent remembers its name and previous messages.
    def createAgent(self, agentname, agentmodel, systemprompt):
        self.agents[agentname] = Agent(agentname, agentmodel, systemprompt, self.client)
        return self.agents[agentname] 
    
    # get a particular agent by name
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
    
    
    
    
    
class Agent:
            
    def __init__(self, agentname, inputmodel, systemprompt, newClient):
        systemprompt = "Your name is " + agentname + ". " + systemprompt
        
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
        max_tokens = 2000 * 5 # about 10000 characters

        # get the message logs
        message_logs = self.message_logs
        
        # get the total amount of tokens in the message logs
        total_tokens = 0
        for message in message_logs:
            total_tokens += len(message["content"].split(" "))
        
        print("Total tokens: " + str(total_tokens))
        
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
        
        # Generating the prompt for the legacy chat completion
        prompt = "\n".join([msg["content"] for msg in self.message_logs])
        
        response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=2048  # You can adjust this value as needed
        )
        
        # Extracting the response and usage information
        agentResponse = response.choices[0].text

        return agentResponse
    
    # insert a message into the message history of the agent without calling the API.
    # this is useful to provide context to ensure more relevant responses from the API later.
    # after inserting the message, we will insert a reaffirming message from the agent to ensure it latches onto the context.
    def addContext(self, message):
        dprint(f"Context Added: {message}")
        self.message_logs.append({"role": "system", "content": "Context: " + message})
        
    # sometimes neccessary to reinforce format
    def addAssistantMessage(self, message):
        self.message_logs.append({"role": "assistant", "content": message})
    
