import time
from model import train_step, train_loss, train_accuracy, ckpt_manager
from constant import EPOCHS
from tokenizer import train_dataset
import logging
from model import transformer
import tensorflow as tf
from func import create_masks

logger = logging.getLogger(__name__)

f_handler = logging.FileHandler("./static/train_model.log")
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


def train():
    for epoch in range(EPOCHS):
        start = time.time()

        train_loss.reset_states()
        train_accuracy.reset_states()

        # inp -> non_diacritic, tar -> diacritic
        for (batch, (inp, tar)) in enumerate(train_dataset):
            train_step(inp, tar)
            if batch % 50 == 0:
                logger.info(
                    "Epoch {} Batch {} Loss {:.4f} Accuracy {:.4f}".format(
                        epoch + 1, batch, train_loss.result(), train_accuracy.result()
                    )
                )

        if (epoch + 1) % 5 == 0:
            ckpt_save_path = ckpt_manager.save()
            logger.info(
                "Saving checkpoint for epoch {} at {}".format(epoch + 1, ckpt_save_path)
            )

        logger.info(
            "Epoch {} Loss {:.4f} Accuracy {:.4f}".format(
                epoch + 1, train_loss.result(), train_accuracy.result()
            )
        )
        logger.info("Time taken for 1 epoch: {} secs\n".format(time.time() - start))


def load_model_from_weight():
    inp = tf.keras.Input(shape=(40))
    tar_inp = tf.keras.Input(shape=(40))
    enc_padding_mask, combined_mask, dec_padding_mask = create_masks(inp, tar_inp)
    transformer(inp=inp, tar=tar_inp, training=True, enc_padding_mask=enc_padding_mask, look_ahead_mask=combined_mask, dec_padding_mask=dec_padding_mask)
    transformer.load_weights("./static/weight_200epochs.h5")
    return transformer