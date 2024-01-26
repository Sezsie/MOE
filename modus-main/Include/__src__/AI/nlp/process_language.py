import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Sample text
text = "Apple Inc. is an American multinational technology company headquartered in Cupertino, California."

# Tokenization
tokens = word_tokenize(text)

# Part-of-Speech Tagging
pos_tags = pos_tag(tokens)

# Named Entity Recognition
named_ents = ne_chunk(pos_tags)

print("Tokens:", tokens)
print("Part-of-Speech Tags:", pos_tags)
print("Named Entities:", named_ents)
