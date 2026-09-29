"""from https://github.com/keithito/tacotron

Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
"""

from typing import Protocol
import logging
import re
import threading

import phonemizer
import phonemizer.backend
from unidecode import unidecode

_worker_phonemizer = None

class ProCleaners(Protocol):
    def clean(self, text: str) -> str:
        pass
    def deload(self):
        pass
    def reload(self):
        pass

class EnglishCleaner2(ProCleaners):
    def __init__(self):
        self.critical_logger = logging.getLogger("phonemizer")
        self.critical_logger.setLevel(logging.CRITICAL)
        # FIXME: The EspeakApi will copy itself after it is forked.
        # But it will clean itself if the reference is dead
        self.phonemizer = phonemizer.backend.EspeakBackend(
            language="en-us",
            preserve_punctuation=True,
            with_stress=True,
            language_switch="remove-flags",
            logger=self.critical_logger
        )
    def clean(self, text: str) -> str:
        """Pipeline for English text, including abbreviation expansion. + punctuation + stress"""
        text = convert_to_ascii(text)
        text = lowercase(text)
        text = expand_abbreviations(text)
        assert self.phonemizer is not None
        phonemes = self.phonemizer.phonemize([text], strip=True, njobs=1)[0]
        # Added in some cases espeak is not removing brackets
        phonemes = remove_brackets(phonemes)
        phonemes = collapse_whitespace(phonemes)
        return phonemes
    def deload(self):
        del self.phonemizer
        self.phonemizer = None
    def reload(self):
        if self.phonemizer is not None:
            del self.phonemizer
            self.phonemizer = None
        self.phonemizer = phonemizer.backend.EspeakBackend(
            language="en-us",
            preserve_punctuation=True,
            with_stress=True,
            language_switch="remove-flags",
            logger=self.critical_logger
        )
class BasicCleaners(ProCleaners):
    def __init__(self):
        pass
    def clean(self, text: str) -> str:
        """Basic pipeline that lowercases and collapses whitespace without transliteration."""
        text = lowercase(text)
        text = collapse_whitespace(text)
        return text

class TransliterationCleaners(ProCleaners):
    def __init__(self):
        pass
    def clean(self, text: str) -> str:
        """Pipeline for non-English text that transliterates to ASCII."""
        text = convert_to_ascii(text)
        text = lowercase(text)
        text = collapse_whitespace(text)
        return text
# Regular expression matching whitespace:
_whitespace_re = re.compile(r"\s+")

# Remove brackets
_brackets_re = re.compile(r"[\[\]\(\)\{\}]")

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [
    (re.compile(f"\\b{x[0]}\\.", re.IGNORECASE), x[1])
    for x in [
        ("mrs", "misess"),
        ("mr", "mister"),
        ("dr", "doctor"),
        ("st", "saint"),
        ("co", "company"),
        ("jr", "junior"),
        ("maj", "major"),
        ("gen", "general"),
        ("drs", "doctors"),
        ("rev", "reverend"),
        ("lt", "lieutenant"),
        ("hon", "honorable"),
        ("sgt", "sergeant"),
        ("capt", "captain"),
        ("esq", "esquire"),
        ("ltd", "limited"),
        ("col", "colonel"),
        ("ft", "fort"),
    ]
]


def expand_abbreviations(text: str) -> str:
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


def lowercase(text: str) -> str:
    return text.lower()


def remove_brackets(text: str) -> str:
    return re.sub(_brackets_re, "", text)


def collapse_whitespace(text: str) -> str:
    return re.sub(_whitespace_re, " ", text)


def convert_to_ascii(text: str) -> str:
    return unidecode(text)


def ipa_simplifier(text: str) -> str:
    replacements = [
        ("ɐ", "ə"),
        ("ˈə", "ə"),
        ("ʤ", "dʒ"),
        ("ʧ", "tʃ"),
        ("ᵻ", "ɪ"),
    ]
    for replacement in replacements:
        text = text.replace(replacement[0], replacement[1])
    phonemes = collapse_whitespace(text)
    return phonemes


# I am removing this due to incompatibility with several version of python
# However, if you want to use it, you can uncomment it
# and install piper-phonemize with the following command:
# pip install piper-phonemize

# import piper_phonemize
# def english_cleaners_piper(text):
#     """Pipeline for English text, including abbreviation expansion. + punctuation + stress"""
#     text = convert_to_ascii(text)
#     text = lowercase(text)
#     text = expand_abbreviations(text)
#     phonemes = "".join(piper_phonemize.phonemize_espeak(text=text, voice="en-US")[0])
#     phonemes = collapse_whitespace(phonemes)
#     return phonemes
