#############################################################################################################
# CLASS DOCUMENTATION
#############################################################################################################
# AUTHOR: Garrett Thrower, Brian Boggs, Colby McClure
# LAST UPDATED: 2024-15-04
# FUNCTION: This class is responsible for classifying text data into two categories: "command" or "conversational".
# The classifier is trained on a dataset of text data specifically curated for this purpose. Is also contains
# helper methods for preprocessing and cleaning text data.
#############################################################################################################

import os
import pickle
import re

from __src__.UTILS.utils import Utilities, DebuggingUtilities, FileUtilities

# might as well import punkt
import nltk

# if punkt isnt installed, install it
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
# get the stopwords
try:
    stopwords = nltk.corpus.stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
    
# get the stemmer
try:
    stemmer = nltk.PorterStemmer()
except LookupError:
    nltk.download('stopwords')
    stemmer = nltk.PorterStemmer()

utils = Utilities()
debug = DebuggingUtilities()
dprint = debug.dprint

class RequestClassifier:
    # initialize the AIHandler class with the API key.
    # AIHandler is the main class that handles all created agents, with a suite of functions to create, delete, and get agents.
    def __init__(self):
        self.classifier = None
        self.vectorizer = None
        self.loadModel()
        
    # load the model from the saved pickle file
    def loadModel(self):
        dir = os.path.join(FileUtilities.getProjectDirectory(), "__ml__")
        self.classifier = pickle.load(open(os.path.join(dir, "MODUS_MODEL.pkl"), "rb"))
        self.vectorizer = pickle.load(open(os.path.join(dir, "MODUS_VECTORIZER.pkl"), "rb"))
      
    # preprocess the text data  
    def preprocess(self, text):
        # clean text of all punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # make all text lowercase
        text = text.lower()
        # remove stopwords
        text = ' '.join([word for word in text.split() if word not in stopwords])
        # stem the words
        text = ' '.join([stemmer.stem(word) for word in text.split()])
        return text
        
    # classify the text data   
    def classify(self, text):
        # preprocess the text
        text = self.preprocess(text)
        
        # if theres only one word, return conversational
        if len(text.split()) == 1:
            return "conversational"
        
        # vectorize the text
        vectorized_text = self.vectorizer.transform([text])
        # classify the text
        prediction = self.classifier.predict(vectorized_text)

        # return the classification
        if prediction[0] == 0:
            return "command"
        elif prediction[0] == 1:
            return "conversational"
        

# special thanks to Brian Boggs and Colby McClure for their contributions to this class.
# without you guys, the research and development of this classifier would not have been possible.
# it may not be perfect, but it's a start.
# thank you for your hard work and dedication to this project.