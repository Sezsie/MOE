import torch
from transformers import AutoTokenizer, AutoModel
from __src__.AI.nlp.classifier import RequestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# a class that uses TinyBERT to get embeddings and calculate similarity between texts
# I might extend this class to include more functionality in the future, but for now it's just for getting embeddings and calculating similarity

# load TinyBERT tokenizer and model (a pretrained model since I don't have the time to train one myself right now)
tok = AutoTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
mod = AutoModel.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')

classifier = RequestClassifier()

class TinyBERT:
    def __init__(self):
        self.model = mod
        self.tok = tok
        pass

    def encode(self, text):
        # encode the text
        encoded_input = self.tok(text, return_tensors='pt')
        return encoded_input

    def embed(self, text):
        # encode the text
        encoded_input = self.encode(text)
        # pass the input to the model
        output = self.model(**encoded_input)
        # return the output
        return output.last_hidden_state

    def get_embedding(self, text):
        # get the embedding
        embedding = self.embed(text)
        # return the embedding
        return embedding

    def get_embeddings(self, texts):
        # get the embeddings for each text
        embeddings = [self.embed(text) for text in texts]
        # return the embeddings
        return embeddings
    
    def how_similar(self, text1, text2):
        # clean the texts
        text1 = classifier.preprocess(text1)
        text2 = classifier.preprocess(text2)
        
        # get the embeddings for both texts
        embedding1 = self.get_embedding(text1).squeeze(0)  # remove the batch dimension
        embedding2 = self.get_embedding(text2).squeeze(0)

        # calculate the mean across the token dimension to get a single vector per string
        embedding1_mean = torch.mean(embedding1, dim=0)
        embedding2_mean = torch.mean(embedding2, dim=0)

        # calculate the cosine similarity
        similarity = torch.nn.functional.cosine_similarity(embedding1_mean.unsqueeze(0), embedding2_mean.unsqueeze(0))
        # return the similarity
        return similarity.item()
    
    def batch_similarity(self, text, texts, threshold):
        # if texts is empty, return None
        if not texts:
            return None, None
        print(f"Texts: {texts}")
        
        # clean the text
        text = classifier.preprocess(text)
        texts = [classifier.preprocess(t) for t in texts]

        # create a TfidfVectorizer
        vectorizer = TfidfVectorizer()
        
        print(f"Creating tfidf matrix for text: {text}")

        # fit the vectorizer on the texts and transform the texts into tf-idf vectors
        tfidf_matrix = vectorizer.fit_transform([text] + texts)

        # calculate the cosine similarity between the text and each text in the list
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix).flatten()

        # find the index of the most similar text
        max_similarity = max(cosine_similarities[1:])  # exclude the first item because it's the similarity with itself
        most_similar_index = cosine_similarities[1:].argmax()
        
        
        print(f"Max similarity: {max_similarity}")

        # check if the highest similarity is below the threshold
        if max_similarity < threshold:
            print(f"No similar text found with similarity above {threshold}")
            return None, None
        else:
            return max_similarity, texts[most_similar_index]


    