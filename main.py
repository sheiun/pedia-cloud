from pprint import pprint

from base import PediaDictionary
from tools import get_all_combinations

print = pprint

if __name__ == "__main__":
    # words = PediaDictionary.get_all_annotations("無")
    # print(words)
    ants = get_all_combinations("無所畏懼")
    ant = PediaDictionary.get_first_annotation("無所畏懼")
    print(ant)
    print(ants)
