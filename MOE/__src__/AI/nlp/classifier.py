#############################################################################################################
# CLASS DOCUMENTATION
#############################################################################################################
# AUTHOR: Sabrina Finch, Brian Boggs, Colby McClure
# LAST UPDATED: 2024-15-04
# FUNCTION: This class is responsible for classifying text data into two categories: "command" or "conversational".
# The classifier is trained on a dataset of text data specifically curated for this purpose. Is also contains
# helper methods for preprocessing and cleaning text data.
#############################################################################################################

import os

import pickle
import re

# might as well import punkt
import nltk

try:
    nltk.data.find('tokenizers/punkt')
    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = nltk.PorterStemmer()
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    stemmer = nltk.PorterStemmer()

class RequestClassifier:
    # initialize the AIHandler class with the API key.
    # AIHandler is the main class that handles all created agents, with a suite of functions to create, delete, and get agents.
    def __init__(self):
        self.classifier = None
        self.vectorizer = None
        self.loadModel()
        
    # load the model from the saved pickle file
    def loadModel(self):
        dir = os.path.join("MOE", "__resources__", "ml")
        self.classifier = pickle.load(open(os.path.join(dir, "MOE_MODEL.pkl"), "rb"))
        self.vectorizer = pickle.load(open(os.path.join(dir, "MOE_VECTORIZER.pkl"), "rb"))
        self.lda = pickle.load(open(os.path.join(dir, "MOE_LDA.pkl"), "rb"))
      
    # preprocess the text data  
    def preprocess(self, text):
        # clean text of all punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # make all text lowercase
        text = text.lower()
        # remove stopwords
        # text = ' '.join([word for word in text.split() if word not in stopwords])
        # stem the words
        # text = ' '.join([stemmer.stem(word) for word in text.split()])
        return text
         
    # classify the input text as either a command or conversational
    def classify(self, text):
        # preprocess and vectorize the text
        preprocessed_text = self.preprocess(text)
        # vectorize the sentence
        vectorized_sentence = self.vectorizer.transform([preprocessed_text])
    
        # transform the sentence using the lda model
        lda_transformed_sentence = self.lda.transform(vectorized_sentence.toarray())
    
        # predict the sentence
        prediction = self.classifier.predict(lda_transformed_sentence)

        # return the classification
        if prediction[0] == 0:
            return "command"
        elif prediction[0] == 1:
            return "conversational"
        

# special thanks to Brian Boggs and Colby McClure for their contributions to this class.
# without you guys, the research and development of this classifier would not have been possible.
# it may not be perfect, but it's a start.
# thank you for your hard work and dedication to this project.
