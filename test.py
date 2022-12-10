from constant import MAX_LENGTH, tokenizer_ipt, tokenizer_opt
import tensorflow as tf
from func import create_masks
from train_model import load_model_from_weight
from tokenizer import test_data
import numpy as np
import phunspell
from load_model import transformer
import unidecode
import string
import pandas as pd
from predict import predict_sentence
import time

def evaluate(inp_sentence):
    start_token = [tokenizer_ipt.vocab_size]
    end_token = [tokenizer_ipt.vocab_size + 1]

    # inp sentence is non_diacritic, hence adding the start and end token
    inp_sentence = start_token + tokenizer_ipt.encode(inp_sentence) + end_token
    encoder_input = tf.expand_dims(inp_sentence, 0)

    # as the target is exist diacritic, the first word to the transformer should be the
    # english start token.
    decoder_input = [tokenizer_opt.vocab_size]
    output = tf.expand_dims(decoder_input, 0)
    for i in range(MAX_LENGTH):
        enc_padding_mask, combined_mask, dec_padding_mask = create_masks(
            encoder_input, output
        )
        predictions, attention_weights = transformer(
            encoder_input,
            output,
            False,
            enc_padding_mask,
            combined_mask,
            dec_padding_mask
        )
        # select the last word from the seq_len dimension
        predictions = predictions[:, -1:, :]  # (batch_size, 1, vocab_size)
        predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)
        # return the result if the predicted_id is equal to the end token
        if predicted_id == tokenizer_opt.vocab_size + 1:
            return tf.squeeze(output, axis=0), attention_weights

        # concatentate the predicted_id to the output which is given to the decoder
        # as its input.
        output = tf.concat([output, predicted_id], axis=-1)

    return tf.squeeze(output, axis=0), attention_weights

def translate(sentence, plot=''):
    result, attention_weights = evaluate(sentence)
    predicted_sentence = tokenizer_opt.decode([i for i in result 
                                            if i < tokenizer_opt.vocab_size])  
    return predicted_sentence

def remove_random_accent(text, ratio=1): 
    words = text.split()
    mask = np.random.random(size=len(words)) < ratio
    for i in range(len(words)):
        if mask[i]:
            words[i] = unidecode.unidecode(words[i])
    return ' '.join(words)

inp = test_data['input'].values
tar = test_data['output'].values
inp = np.array([" ".join(val.split(" ")[:38]) for val in inp])
tar = np.array([" ".join(val.split(" ")[:38]) for val in tar])
tar_data = []
for val in tar:
    temp = val.translate(str.maketrans("", "", string.punctuation))
    temp = [val for val in temp.split(" ") if val != ""]
    temp = " ".join(temp)
    tar_data.append(temp)
inp_data = pd.read_csv("data_no_punctuation.csv")
predict_texts = []
start_time = time.time()
for idx, val in enumerate(inp_data["0"].values):
    predict_texts.append(predict_sentence(val))
    if (idx + 1) % 100 == 0:
        print(f"idx: {idx} === {time.time() - start_time}")
        start_time = time.time()
predict_texts = pd.DataFrame(predict_texts)
predict_texts.to_csv("predict_texts.csv", index=False)
print(predict_texts)