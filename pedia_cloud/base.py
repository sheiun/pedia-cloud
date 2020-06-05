from __future__ import annotations

import re
from json import loads
from typing import Dict, List, Optional

import requests

from .error import ApiError


class Word:
    meta: dict
    meanings: List[Meaning]

    def __init__(self, text, meta):
        self.text = text
        self.meta = meta
        self.meanings = []
        for d in self.meta["definitions"]:
            # NOTE: clean `[二]ㄇㄛˊ　mó`
            if r"　" not in d["def"] and self.zuyin not in d["def"]:
                self.meanings.append(self.Meaning(d))

    def __repr__(self):
        return ", ".join(
            [self.text, self.zuyin, f"meanings count: {len(self.meanings)}"]
        )

    @property
    def zuyin(self) -> str:
        return self.meta["bopomofo"]

    @property
    def pinyin(self) -> str:
        return self.meta["pinyin"]

    @property
    def annotations(self) -> List[str]:
        _annotations = [meaning.annotation for meaning in self.meanings]
        # XXX: Not sure if _annotations will be empty or not
        if len(_annotations) == 0:
            raise ApiError("No annotation!")
        return _annotations

    def filter_by_pos(self, poss: List[str]) -> List[Meaning]:
        return list(filter(lambda m: m.pos in poss, self.meanings))

    class Meaning(dict):
        cached_refs: Dict[str, str] = {}

        @property
        def pos(self) -> Optional[str]:
            try:
                return re.search(r"\[(.*)\].*", self["type"]).group(1)
            except KeyError:
                return None

        @property
        def annotation(self) -> str:
            idx = self.full.find("。")
            # NOTE: detect 見「xxx」條
            match = self.has_ref()
            if match:
                return self.get_ref(match)
            if idx > 0:
                return self.full[: idx + 1]
            return self.full

        def has_ref(self) -> Optional[re.match]:
            return re.search(r"見「(.*)」條.*", self.full)

        def get_ref(self, match):
            word = match.group(1)
            if word not in self.cached_refs:
                self.cached_refs[word] = PediaDictionary.get_first_annotation(word)
            return self.cached_refs[word]

        @property
        def full(self) -> str:
            return self["def"]


class PediaDictionary:
    @staticmethod
    def get_all(word: str) -> List[Word]:
        res = requests.get(f"https://pedia.cloud.edu.tw/api/EntryApi/?strEntry={word}")
        json = res.json()
        if not isinstance(json, dict):
            json = loads(json)
        if "Message" in json:
            raise ApiError(json["Message"])
        if "revised_dict" not in json:
            raise ApiError("revised_dict not exist")
        heteronyms = json["revised_dict"]["heteronyms"]
        if not heteronyms:
            raise KeyError(word, "No data in heteronyms!")
        words = [Word(word, h) for h in heteronyms]
        return words

    @classmethod
    def get_all_annotations(cls, word: str):
        words = cls.get_all(word)
        annotations = []
        for word in words:
            annotations.extend(word.annotations)
        return annotations

    @classmethod
    def get_one(cls, word: str) -> Word:
        return cls.get_all(word)[0]

    @classmethod
    def get_first_annotation(cls, word: str) -> str:
        return cls.get_one(word).annotations[0]

    @classmethod
    def segment(cls, word: str) -> List[str]:
        parts = []
        for window in range(len(word) - 1, 1, -1):
            for position in range(0, len(word) - window + 1):
                # NOTE: overlay checking
                if any([p[0] <= position < p[1] for p in parts]):
                    continue
                current = word[position : position + window]
                try:
                    PediaDictionary.get_one(current)
                except ApiError:
                    continue
                parts.append((position, position + window))
        parts.sort(key=lambda x: x[0])

        indices = []
        p = 0
        for i, j in parts:
            while i > p:
                indices.append((p, p + 1))
                p += 1
            indices.append((i, j))
            p = i + j
        while p < len(word):
            indices.append((p, p + 1))
            p += 1
        return [word[i:j] for i, j in indices]
