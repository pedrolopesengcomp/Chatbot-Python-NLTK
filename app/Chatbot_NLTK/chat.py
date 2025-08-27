import random
import json
import torch
import nltk
from pathlib import Path 

from app.Chatbot_NLTK.model import NeuralNet
from app.Chatbot_NLTK.nltk_utils import bag_of_words, tokenize, stem

# Baixando recursos nltk
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find("stemmers/rslp")
except LookupError:
    nltk.download("punkt")
    nltk.download("rslp")

# Dados json
with open( Path(__file__).parent / 'perguntasRespostas.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

# Dados treinados
FILE =  Path(__file__).parent / "chatdata.pth"
try:
    data = torch.load(FILE, weights_only=False)
except Exception as e:
    print(f"Erro ao carrega r o modelo: {e}")
    exit()

# Configurar modelo
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)

# Dispositivo
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def get_response(msg):
    try:
        # Tokenizar mensagem
        sentence_tokens = tokenize(msg)
        x = bag_of_words(sentence_tokens, all_words)
        x = x.reshape(1, x.shape[0])
        x = torch.from_numpy(x).to(device)

        output = model(x)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]

        # Probabilidade
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        # Responder caso tenha uma posibilidade alta
        if prob.item() > 0.75:
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    return random.choice(intent['responses'])
        return "Nao entendi... Poderia reformular?"
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        return "Ocorreu um erro interno. Por favor, tente novamente."