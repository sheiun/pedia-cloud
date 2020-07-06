from unittest import TestCase

from pedia_cloud import PediaDictionary


class TestSegement(TestCase):
    def test_segment(self):
        self.assertEqual(PediaDictionary.segment("一鳴驚人"), ["一", "鳴", "驚人"])
        self.assertEqual(PediaDictionary.segment("一毛不拔"), ["一毛", "不拔"])
        self.assertEqual(PediaDictionary.segment("胸有成竹"), ["胸", "有成", "竹"])
        self.assertEqual(PediaDictionary.segment("打退堂鼓"), ["打", "退堂鼓"])
