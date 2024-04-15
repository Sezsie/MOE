import torch
from transformers import AutoTokenizer, AutoModel
from __src__.AI.nlp.classifier import RequestClassifier

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
    
    def batch_similarity(self, text, texts, threshold=0.85):
        # if texts is empty, return None
        if not texts:
            return None, None
        
        # clean the text
        text = classifier.preprocess(text)
        
        # get the embedding for the text
        embedding = self.get_embedding(text).squeeze(0)
        embedding_mean = torch.mean(embedding, dim=0)

        # get the embeddings for the list of texts
        embeddings = self.get_embeddings(texts)
        mean_embeddings = [torch.mean(emb.squeeze(0), dim=0) for emb in embeddings]

        # calculate the cosine similarity between the text and each text in the list
        similarities = [torch.nn.functional.cosine_similarity(embedding_mean.unsqueeze(0), mean_emb.unsqueeze(0), dim=1).item() for mean_emb in mean_embeddings]
        # find the index of the most similar text
        max_similarity = max(similarities)
        most_similar_index = similarities.index(max_similarity)

        # check if the highest similarity is below the threshold
        if max_similarity < threshold:
            return None, None
        else:
            return max_similarity, texts[most_similar_index]


    