"""from https://github.com/keithito/tacotron"""

from matcha.text import cleaners
from matcha.text.cleaners import ProCleaners
from matcha.text.symbols import symbols
from typing import List, Tuple

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}  # pylint: disable=unnecessary-comprehension

class UnknownCleanerException(Exception):
    pass

class Cleaner:
    def __init__(self, cleaner_names: List[str]):
        self.cleaners: List[ProCleaners] = []
        for name in cleaner_names:
            cleaner = getattr(cleaners, name)
            self.cleaners.append(cleaner())
    def text_to_sequence(self, text: str) -> Tuple[List[int], str]:
        """Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
        Args:
          text: string to convert to a sequence
          cleaner_names: names of the cleaner functions to run the text through
        Returns:
          List of integers corresponding to the symbols in the text
        """
        clean_text = text
        sequence = []
        for cleaner in self.cleaners:
            clean_text = cleaner.clean(clean_text)
        for symbol in clean_text:
            symbol_id = _symbol_to_id[symbol]
            sequence += [symbol_id]
        return sequence, clean_text
    def deload(self):
        for cleaner in self.cleaners:
            cleaner.deload()
    def reload(self):
        for cleaner in self.cleaners:
            cleaner.reload()

def cleaned_text_to_sequence(cleaned_text: List[str]) -> List[int]:
    """Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
    Args:
      text: string to convert to a sequence
    Returns:
      List of integers corresponding to the symbols in the text
    """
    sequence = [_symbol_to_id[symbol] for symbol in cleaned_text]
    return sequence


def sequence_to_text(sequence: List[int]) -> str:
    """Converts a sequence of IDs back to a string"""
    result = ""
    for symbol_id in sequence:
        s = _id_to_symbol[symbol_id]
        result += s
    return result

