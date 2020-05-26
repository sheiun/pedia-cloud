from .base import PediaDictionary


def get_all_combinations(idiom: str):
    # cut words
    words = list(idiom)
    ants_lst = [PediaDictionary.get_all_annotations(word) for word in words]
    return ants_lst
