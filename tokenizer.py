import pandas as pd
import tensorflow as tf
import pickle
import tensorflow_datasets as tfds
import constant

train_data = pd.read_csv("./static/train_data.csv")
train_input = train_data["input"]
train_output = train_data["output"]
train_index = train_data["index"]
val_data = pd.read_csv("./static/val_data.csv")
val_input = val_data["input"]
val_output = val_data["output"]
val_index = val_data["index"]
test_data = pd.read_csv("./static/test_data.csv")
test_input = test_data["input"]
test_output = test_data["output"]
test_index = test_data["index"]

train_examples = tf.data.Dataset.from_tensor_slices((train_input, train_output))
val_examples = tf.data.Dataset.from_tensor_slices((val_input, val_output))


def build_tokenzier():
    tokenizer_ipt = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
        (ipt.numpy() for (ipt, opt) in train_examples), target_vocab_size=2**13
    )

    tokenizer_opt = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
        (opt.numpy() for (ipt, opt) in train_examples), target_vocab_size=2**13
    )
    return tokenizer_ipt, tokenizer_opt

def _save_pickle(path, obj):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def save_tokenizer(tokenizer_ipt, tokenizer_opt):
    _save_pickle('./tokenizer_input.pkl', tokenizer_ipt)
    _save_pickle('./tokenizer_output.pkl', tokenizer_opt)

def encode(ipt, opt):
    tokenizer_ipt = constant.tokenizer_ipt
    tokenizer_opt = constant.tokenizer_opt
    ipt = [tokenizer_ipt.vocab_size] + tokenizer_ipt.encode(
        ipt.numpy()) + [tokenizer_ipt.vocab_size+1]

    opt = [tokenizer_opt.vocab_size] + tokenizer_opt.encode(
        opt.numpy()) + [tokenizer_opt.vocab_size+1]
    return ipt, opt

def tf_encode(ipt, opt):
    result_ipt, result_opt = tf.py_function(encode, [ipt, opt], [tf.int64, tf.int64])
    result_ipt.set_shape([None])
    result_opt.set_shape([None])
    return result_ipt, result_opt

def filter_max_length(x, y, max_length=constant.MAX_LENGTH):
    return tf.logical_and(tf.size(x) <= max_length,
                        tf.size(y) <= max_length)
  
train_dataset = train_examples.map(tf_encode)
train_dataset = train_dataset.filter(filter_max_length)
# cache the dataset to memory to get a speedup while reading from it.
train_dataset = train_dataset.cache()
train_dataset = train_dataset.shuffle(constant.BUFFER_SIZE).padded_batch(constant.BATCH_SIZE)
train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

val_dataset = val_examples.map(tf_encode)
val_dataset = val_dataset.filter(filter_max_length).padded_batch(constant.BATCH_SIZE)
