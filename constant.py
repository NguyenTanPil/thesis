import pickle
from unittest.util import _MAX_LENGTH

def _load_pickle(path):
    with open(path, 'rb') as f:
        obj = pickle.load(f)
    return obj

tokenizer_ipt = _load_pickle("./static/tokenizer_input.pkl")
tokenizer_opt = _load_pickle("./static/tokenizer_output.pkl")

NUM_LAYERS = 4
D_MODEL = 128
DFF = 512
NUM_HEADS = 8

INPUT_VOCAB_SIZE = tokenizer_ipt.vocab_size + 2
TARGET_VOCAB_SIZE = tokenizer_opt.vocab_size + 2
DROPOUT_RATE = 0.1
EPOCHS = 100
BUFFER_SIZE = 20000
BATCH_SIZE = 24
MAX_LENGTH = 40