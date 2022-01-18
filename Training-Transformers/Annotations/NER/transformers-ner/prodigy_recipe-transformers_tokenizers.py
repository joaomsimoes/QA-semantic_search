from typing import List, Optional, Dict, Any
from tokenizers import BertWordPieceTokenizer
from prodigy.components.loaders import get_stream
from prodigy.util import get_labels
import prodigy

from elasticsearchprodigy import search


@prodigy.recipe(
    "bert.ner.manual",
    dataset=("Dataset to save annotations to", "positional", None, str),
    coin=("coin to annotate", "positional", None, str),
    label=("Comma-separated label(s) to annotate or text file with one label per line", "option", "l", get_labels),
    tokenizer_vocab=("Tokenizer vocab file", "option", "tv", str),
    lowercase=("Set lowercase=True for tokenizer", "flag", "LC", bool),
    hide_special=("Hide SEP and CLS tokens visually", "flag", "HS", bool),
    hide_wp_prefix=("Hide wordpieces prefix like ##", "flag", "HW", bool),
    # fmt: on
)
def ner_manual_tokenizers_bert(
        dataset: str,
        coin: str,
        label: Optional[List[str]] = None,
        tokenizer_vocab: Optional[str] = None,
        lowercase: bool = False,
        hide_special: bool = False,
        hide_wp_prefix: bool = False,
) -> Dict[str, Any]:
    """Example recipe that shows how to use model-specific tokenizers like the
    BERT word piece tokenizer to preprocess your incoming text for fast and
    efficient NER annotation and to make sure that all annotations you collect
    always map to tokens and can be used to train and fine-tune your model
    (even if the tokenization isn't that intuitive, because word pieces). The
    selection automatically snaps to the token boundaries and you can double-click
    single tokens to select them.
    Setting "honor_token_whitespace": true will ensure that whitespace between
    tokens is only shown if whitespace is present in the original text. This
    keeps the text readable.
    Requires Prodigy v1.10+ and usese the HuggingFace tokenizers library."""
    search(coin)
    stream = get_stream('coin_reddit.txt')
    # You can replace this with other tokenizers if needed
    tokenizer = BertWordPieceTokenizer(tokenizer_vocab, lowercase=lowercase)
    sep_token = tokenizer._parameters.get("sep_token")
    cls_token = tokenizer._parameters.get("cls_token")
    special_tokens = (sep_token, cls_token)
    wp_prefix = tokenizer._parameters.get("wordpieces_prefix")

    def add_tokens(stream):
        for eg in stream:
            tokens = tokenizer.encode(eg["text"])
            eg_tokens = []
            idx = 0
            for (text, (start, end), tid, type_ids, attention_mask) in zip(
                    tokens.tokens, tokens.offsets, tokens.ids, tokens.type_ids,
                    tokens.attention_mask
            ):
                # If we don't want to see special tokens, don't add them
                if hide_special and text in special_tokens:
                    continue
                # If we want to strip out word piece prefix, remove it from text
                if hide_wp_prefix and wp_prefix is not None:
                    if text.startswith(wp_prefix):
                        text = text[len(wp_prefix) :]
                token = {
                    "text": text,
                    "id": idx,
                    "start": start,
                    "end": end,
                    # This is the encoded ID returned by the tokenizer
                    "tokenizer_id": tid,
                    "type_ids": type_ids,
                    "attention_mask": attention_mask,
                    # Don't allow selecting spacial SEP/CLS tokens
                    "disabled": text in special_tokens,
                }
                eg_tokens.append(token)
                idx += 1
            for i, token in enumerate(eg_tokens):
                # If the next start offset != the current end offset, we
                # assume there's whitespace in between
                if i < len(eg_tokens) - 1 and token["text"] not in special_tokens:
                    next_token = eg_tokens[i + 1]
                    token["ws"] = (
                            next_token["start"] > token["end"]
                            or next_token["text"] in special_tokens
                    )
                else:
                    token["ws"] = True
            eg["tokens"] = eg_tokens
            yield eg

    stream = add_tokens(stream)

    return {
        "dataset": dataset,
        "stream": stream,
        "view_id": "ner_manual",
        "config": {
            "honor_token_whitespace": True,
            "labels": label,
            "exclude_by": "input",
            "force_stream_order": True,
        },
    }
