from typing import Dict, List, Tuple
from tiktoken import get_encoding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase


class OpenAITokenizerWrapper(PreTrainedTokenizerBase):
    def __init__(self, model_name: str = "cl100k_base", max_length: int = 8191, **kwargs):
        super().__init__(model_max_length=max_length, **kwargs)
        self.tokenizer = get_encoding(model_name)
        self._vocab_size = self.tokenizer.n_vocab

    def tokenize(self, text: str, **kwargs) -> List[str]:
        return [str(t) for t in self.tokenizer.encode(text)]

    def _tokenize(self, text: str) -> List[str]:
        return self.tokenize(text)

    def _convert_token_to_id(self, token: str) -> int:
        return int(token)

    def _convert_id_to_token(self, index: int) -> str:
        return str(index)

    def get_vocab(self) -> Dict[str, int]:
        return {str(i): i for i in range(self._vocab_size)}

    @property
    def vocab_size(self) -> int:
        return self._vocab_size

    def save_vocabulary(self, *args) -> Tuple[str]:
        return ()

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()

    def __len__(self):
        return self._vocab_size
