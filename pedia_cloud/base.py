from __future__ import annotations

import re
from collections import Counter
from json import loads
from typing import Dict, List, Optional, Counter as CounterT

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
            # NOTE: 這行是因為 `罵` 的解釋摻雜
            d["def"] = d["def"].replace(r"　", "")
            # NOTE: clean `[二]ㄇㄛˊ　mó`
            if not self.includes_zuyin(d["def"]):
                self.meanings.append(self.Meaning(d))

    @staticmethod
    def includes_zuyin(text: str) -> bool:
        """Text includes zuyin (ㄅ~ㄦ ˊˇˋ˙)

        Args:
            text (str)

        Returns:
            bool
        """
        return bool(re.search(r"[\u3105-\u3129\u02CA\u02C7\u02CB\u02D9]", text))

    def __repr__(self):
        return ", ".join(
            [self.text, self.zuyin, f"meanings count: {len(self.meanings)}"]
        )

    @property
    def has_meaning(self) -> bool:
        return not all([m.has_ref() for m in self.meanings])

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
            # NOTE: detect 見「xxx」條
            match = self.has_ref()
            if match:
                return self.get_ref(match)
            idx = self.full.find("。")
            if idx > 0:
                return self.full[: idx + 1]
            return self.full

        def has_ref(self) -> Optional[re.match]:
            # FIXME: 參見「瓏玲」、「瓏瓏」等條。
            # Correct: 瓏玲, 瓏瓏
            # Current: 瓏玲」、「瓏瓏
            match = re.search(r"見「(.*)」等?條.*", self.full)
            if match:
                return match
            return re.search(r"通「(.*)」", self.full)

        def get_ref(self, match):
            word = match.group(1)
            # FIXME: due to has_ref's problem
            word = word.split("、")[0].strip("「").strip("」")
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
            raise ApiError(word, json["Message"])
        if "revised_dict" not in json:
            raise ApiError(word, "revised_dict not exist")
        heteronyms = json["revised_dict"]["heteronyms"]
        if not heteronyms:
            raise KeyError(word, "No data in heteronyms!")
        words = [Word(word, h) for h in heteronyms]
        return words

    @classmethod
    def get_all_annotations(cls, word: str) -> List[str]:
        words = cls.get_all(word)
        annotations = []
        for word in words:
            annotations.extend(word.annotations)
        return annotations

    @classmethod
    def get_all_poss(cls, word: str) -> CounterT[str, int]:
        words = cls.get_all(word)
        poss = []
        for word in words:
            poss.extend([m.pos for m in word.meanings if m.pos])
        return Counter(poss)

    @classmethod
    def get_one(cls, word: str) -> Word:
        """Get most meaningful one

        Args:
            word (str): Chinese word can be a character.

        Returns:
            Word: Word object
        """
        return max(cls.get_all(word), key=lambda x: len(x.meanings))

    @classmethod
    def get_first_annotation(cls, word: str) -> str:
        return cls.get_one(word).annotations[0]

    @classmethod
    def segment(cls, word: str) -> List[str]:
        parts = []
        for window in range(len(word) - 1, 1, -1):
            for position in range(0, len(word) - window + 1):
                # NOTE: overlay checking
                if any(
                    [
                        p[0] <= position < p[1] or p[0] < position + window < p[1]
                        for p in parts
                    ]
                ):
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
            p = j
        while p < len(word):
            indices.append((p, p + 1))
            p += 1
        return [word[i:j] for i, j in indices]

    @classmethod
    def segment_by_meaning(cls, word: str, max_win_size=3) -> List[str]:
        parts = []  # [(0, 1), (1, 2)]
        others = []  # [(5, 6)]

        window_size = 1
        for idx, char in enumerate(word):
            position = (idx, idx + window_size)
            current = char
            if cls.get_one(current).has_meaning:
                parts.append(position)
            else:
                others.append(position)

        for window_size in range(2, max_win_size + 1):
            dones = []
            for part in others:
                start = part[0]
                end = part[1]
                if part in dones:
                    continue
                if any([p[0] <= start <= p[1] and p[0] <= end <= p[1] for p in parts]):
                    continue

                # TODO: for loop window size
                connected = next((p for p in others if p[0] == end), None)
                if connected:
                    try:
                        if cls.get_one(word[start : connected[1]]).has_meaning:
                            parts.append((start, connected[1]))
                            dones.append((start, end))
                            dones.append((connected[0], connected[1]))
                            continue
                    except ApiError:
                        pass

                # previous
                if not start - (window_size - 1) < 0:
                    sub_word = word[start - (window_size - 1) : end]
                    try:
                        if cls.get_one(sub_word).has_meaning:
                            [
                                parts.remove(p)
                                for p in parts
                                if start - (window_size - 1) <= p[0] <= end
                                and start - (window_size - 1) <= p[1] <= end
                            ]
                            parts.append((start - (window_size - 1), end))
                            dones.append((start, end))
                        continue
                    except ApiError:
                        pass

                # next
                if not end + (window_size - 1) > len(word):
                    sub_word = word[start : end + (window_size - 1)]
                    try:
                        if cls.get_one(sub_word).has_meaning:
                            [
                                parts.remove(p)
                                for p in parts
                                if start <= p[0] <= end + (window_size - 1)
                                and start <= p[1] <= end + (window_size - 1)
                            ]
                            parts.append((start, end + (window_size - 1)))
                            dones.append((start, end))
                    except ApiError:
                        pass
            [others.remove(o) for o in dones]

        parts.sort(key=lambda x: x[0])  # sort by start

        segs = [word[p[0] : p[1]] for p in parts]

        # NOTE: 無法正確斷詞 -> 無法斷詞
        if word == "".join(segs):
            return segs
        print(word)
        return word
