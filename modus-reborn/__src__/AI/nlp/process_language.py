from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch
# NOTE: THIS CODE IS NOT READY FOR PRODUCTION!!! This is simply a test that I used to educate myself a bit on huggingface.
# Load the tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

# Example dataset, a list of sentences with their labels. a jsonl file is also accepted by the Trainer class, and is recommended for larger datasets.
# TODO: figure out how to use a jsonl file with the Trainer class, as well as how to use this model at all.
texts = ["Hey there buddy. Can you do me a favor and launch firefox for me? Thanks.", 
         "Could you please turn off the living room lights?"]
commands = ["launch firefox", "turn off lights"]

# Tokenize the input texts
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
labels = torch.tensor([0, 1])  # Your labels here

# Define a dataset class
class CommandDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# Create the dataset
dataset = CommandDataset(inputs, labels)

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',          
    num_train_epochs=3,              
    per_device_train_batch_size=16,  
    per_device_eval_batch_size=64,   
    warmup_steps=500,                
    weight_decay=0.01,               
    logging_dir='./logs',            
)

# Initialize the Trainer
trainer = Trainer(
    model=model,                         
    args=training_args,                  
    train_dataset=dataset,         
)

# Train the model
trainer.train()
