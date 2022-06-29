import torch
import torch.nn as nn
import numpy as np
import string


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def _init_weeb():
    ALL_LETTERS = string.ascii_letters + " .,;'"
    N_LETTERS = len(ALL_LETTERS)
    
    n_hidden = 128
    all_categories = ['Arabic', 'Chinese', 'Czech', 'Dutch', 'English', 'French', 'German', 'Greek', 'Irish', 'Italian', 'Japanese', 'Korean', 'Polish', 'Portuguese', 'Russian', 'Scottish', 'Spanish', 'Vietnamese']
    
    class RNN(nn.Module):
        # nn.RNN
        def __init__(self, input_size, hidden_size, output_size):
            super().__init__()

            self.hidden_size = hidden_size
            self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
            self.i2o = nn.Linear(input_size + hidden_size, output_size)
            self.softmax = nn.LogSoftmax(dim=1)

        def forward(self, input_tensor, hiddem_tensor):
            combined = torch.cat((input_tensor, hiddem_tensor), dim=1)

            hidden = self.i2h(combined)
            output = self.i2o(combined)

            output = self.softmax(output)
            return output, hidden

        def init_hidden(self):
            return torch.zeros(1, self.hidden_size)
   
    rnn = RNN(N_LETTERS, n_hidden, len(all_categories)).to(device)
    rnn.load_state_dict(torch.load('cogs\model\weeb_classifier'))
    rnn.eval()
    return rnn

class AllModels:
    def __init__(self) -> None:
        self.rnn = _init_weeb()
        
    def predict_weebness(self, name):
        ALL_LETTERS = string.ascii_letters + " .,;'"
        N_LETTERS = len(ALL_LETTERS)
        
        def letter_to_index(letter):
            return ALL_LETTERS.find(letter)
    
        def line_to_tensor(line):
            tensor = torch.zeros(len(line), 1, N_LETTERS)
            for i, letter in enumerate(line):
                tensor[i][0][letter_to_index(letter)] = 1
            return tensor

        def predict(ip):
            with torch.no_grad():
                hidden = self.rnn.init_hidden()
                line_tensor = line_to_tensor(ip)

                for i in  range(line_tensor.size()[0]): # [5, 1, 57]
                    output, hidden = self.rnn(line_tensor[i].to(device), hidden.to(device))
            
                percent = np.round(np.exp(output[0][10].item())*100, decimals=3)

            return ('Japanese', percent)

        score = ('', 0)

        for i in range(len(name)):
            if (s := predict(name[0:i+1]))[1] > score[1]:
                score = s

        return score
        

if __name__ == "__main__":
    allmodels = AllModels()
    print(allmodels.predict_weebness('mikune'))

