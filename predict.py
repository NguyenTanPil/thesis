from operator import index
import phunspell
import numpy as np
import unidecode
import tensorflow as tf
from constant import tokenizer_ipt, tokenizer_opt
from func import create_masks
from load_model import transformer

pspell = phunspell.Phunspell('vi_VN')

def spell_check(text):
    txt = text.split(" ")
    idx = []
    for word in txt:
        idx.append(pspell.lookup(word))
    return pspell.lookup_list(text.split(" ")), idx

def remove_random_accent(text, ratio=1): 
    words = text.split()
    mask = np.random.random(size=len(words)) < ratio
    for i in range(len(words)):
        if mask[i]:
            words[i] = unidecode.unidecode(words[i])
    return ' '.join(words)

def spell_recommend(words: list):
    suggestions = {}
    for word in words:
        suggestions[word] = []
        for suggestion in pspell.suggest(word):
            suggestions[word] += [remove_random_accent(suggestion, 1)]
        suggestions[word] = list(dict.fromkeys(suggestions[word]))
    return suggestions

def replace_none_accent_word(text, idx, recommend_words):
    text_list = text.split(" ")
    for i, value in enumerate(idx):
        if value == False:
            if len(recommend_words[text_list[i]]) != 0:
                text_list[i] = recommend_words[text_list[i]][0]
    return " ".join(text_list)

def predict_next_word(inp_sentence, decoder_input):
    start_token = [tokenizer_ipt.vocab_size]
    end_token = [tokenizer_ipt.vocab_size + 1]
    inp_sentence = start_token + tokenizer_ipt.encode(inp_sentence) + end_token
    encoder_input = tf.expand_dims(inp_sentence, 0)
    output = tf.expand_dims(decoder_input, 0)
    enc_padding_mask, combined_mask, dec_padding_mask = create_masks(encoder_input, output)
    enc_padding_mask, combined_mask, dec_padding_mask = create_masks(encoder_input, output)
    predictions, _ = transformer(encoder_input, 
                                                    output,
                                                    False,
                                                    enc_padding_mask,
                                                    combined_mask,
                                                    dec_padding_mask)
    predictions = predictions[: ,-1:, :]  # (batch_size, 1, vocab_size)
    predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)
    return predicted_id

def add_predict_word(text: str, predict_id, idx):
    sub_text = text.split(" ")
    sub_text[idx] = tokenizer_opt.decode(predict_id).strip()
    return " ".join(sub_text)


def replace_sentence(text, idx):
    while False in idx:
        index = idx.index(False)
        inp_sentence = remove_random_accent(text, 1)
        target_inp = " ".join(text.split(" ")[:index]) + " "
        decoder_input = [tokenizer_opt.vocab_size] + tokenizer_opt.encode(target_inp)
        if index == 0:
            decoder_input = [tokenizer_opt.vocab_size]
        predict_id = predict_next_word(inp_sentence, decoder_input)
        text = add_predict_word(text, predict_id[0], index)
        idx[index] = True
    return text

def predict_sentence(text):
    wrong_words, idx = spell_check(text)
    recommend_words = spell_recommend(wrong_words)
    replace_text = replace_none_accent_word(text, idx, recommend_words)
    predict_text = replace_sentence(replace_text, idx)
    return predict_text