import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize, stem
import nltk

class ChatBot:

    def __init__(self):
        # Baixando recursos nltk
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find("stemmers/rslp")
        except LookupError:
            nltk.download("punkt")
            nltk.download("rslp")
        # Dados json
        with open('perguntasRespostas.json', 'r', encoding='utf-8') as f:
            self.intents = json.load(f)

        # Dados treinados
        self.FILE = "chatdata.pth"
        try:
            self.data = torch.load(self.FILE)
        except Exception as e:
            print(f"Erro ao carregar o modelo: {e}")
            exit()

        # Configurar modelo
        self.input_size = self.data["input_size"]
        self.hidden_size = self.data["hidden_size"]
        self.output_size = self.data["output_size"]
        self.all_words = self.data["all_words"]
        self.tags = self.data["tags"]
        self.model_state = self.data["model_state"]

        self.model = NeuralNet(self.input_size, self.hidden_size, self.output_size)
        self.model.load_state_dict(self.model_state)

        # Dispositivo
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def get_response(self, msg):
        try:
            # Tokenizar mensagem
            sentence_tokens = tokenize(msg)
            x = bag_of_words(sentence_tokens, self.all_words)
            x = x.reshape(1, x.shape[0])
            x = torch.from_numpy(x).to(self.device)

            output = self.model(x)
            _, predicted = torch.max(output, dim=1)
            tag = self.tags[predicted.item()]

            # Probabilidade
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]

            # Responder caso tenha uma posibilidade alta
            if prob.item() > 0.75:
                for intent in self.intents["intents"]:
                    if tag == intent["tag"]:
                        return random.choice(intent['responses'])
            return "Nao entendi... Poderia reformular?"
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            return "Ocorreu um erro interno. Por favor, tente novamente."

    print("Chatbot iniciado! Digite 'sair' para encerrar.")

    while True:
        try:
            sentence = input("Voce: ")
            if sentence.lower() in ["sair", "quit", "exit"]:
                print("Chatbot: Até mais!")
                break

            print(f"Chatbot: {get_response(sentence)}")

        except KeyboardInterrupt:
            print("\nChatbot: Até mais!")
            break
        except Exception as e:
            print(f"Erro: {e}")