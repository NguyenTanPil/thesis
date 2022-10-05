from transformers import AutoTokenizer
import numpy as np
from transformers import TFAutoModel
import tensorflow as tf

max_length = 32
tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base')
def bert_encode(data, maximum_length):
    input_ids = []
    attention_masks = []

    for text in data:
        encoded = tokenizer.encode_plus(
            text, 
            add_special_tokens=True,
            max_length=maximum_length,
            pad_to_max_length=True,

            return_attention_mask=True,
        )
        input_ids.append(encoded['input_ids'])
        attention_masks.append(encoded['attention_mask'])
        
    return np.array(input_ids),np.array(attention_masks)
input_ids, attention_masks = bert_encode(data.values.tolist(), max_length)

phobert = TFAutoModel.from_pretrained('vinai/phobert-base')
def create_model(bert_model):
    
    input_ids = tf.keras.Input(shape=(max_length,),dtype='int32', name="input_ids")
    attention_masks = tf.keras.Input(shape=(max_length,),dtype='int32', name="attention_masks")

    output = bert_model([input_ids,attention_masks])
    output = output.last_hidden_state
    
    model = tf.keras.models.Model(inputs = [input_ids,attention_masks],outputs = output)
    return model

phobert = TFAutoModel.from_pretrained('vinai/phobert-base')