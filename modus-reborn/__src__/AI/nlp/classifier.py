#############################################################################################################
# CLASS DOCUMENTATION
#############################################################################################################
# AUTHOR: Garrett Thrower
# LAST UPDATED: 2024-09-04
# FUNCTION: This class is responsible for classifying text data into two categories: "command" or "conversational".
# The classifier is trained on a dataset of text data specifically curated for this purpose. Is also contains
# helper methods for preprocessing and cleaning text data.
#
#############################################################################################################
import os

import pandas as pd
import pickle
import re

from __src__.UTILS.utils import Utilities, DebuggingUtilities


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
        dir = os.path.join("modus-reborn", "__ml__")
        self.classifier = pickle.load(open(os.path.join(dir, "MODUS_MODEL.pkl"), "rb"))
        self.vectorizer = pickle.load(open(os.path.join(dir, "MODUS_VECTORIZER.pkl"), "rb"))
      
    # preprocess the text data  
    def preprocess(self, text):
        # clean text of all punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # make all text lowercase
        text = text.lower()
        return text
        
    # classify the text data   
    def classify(self, text):
        # preprocess the text
        text = self.preprocess(text)
        
        print(f"Preprocessed Text: {text}")
        
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