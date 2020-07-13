from unittest import TestCase

from pedia_cloud import PediaDictionary


class TestSegement(TestCase):
    def test_segment(self):
        self.assertEqual(PediaDictionary.segment("一鳴驚人"), ["一", "鳴", "驚人"])
        self.assertEqual(PediaDictionary.segment("一毛不拔"), ["一毛", "不拔"])
        self.assertEqual(PediaDictionary.segment("胸有成竹"), ["胸", "有成", "竹"])
        self.assertEqual(PediaDictionary.segment("打退堂鼓"), ["打", "退堂鼓"])

    def test_segment_by_meaning(self):
        self.assertEqual(PediaDictionary.segment_by_meaning("囫圇吞棗"), ["囫圇", "吞", "棗"])
        self.assertEqual(PediaDictionary.segment_by_meaning("栩栩如生"), ["栩栩", "如", "生"])
        self.assertEqual(PediaDictionary.segment_by_meaning("戰戰兢兢"), ["戰", "戰", "兢兢"])
        self.assertEqual(PediaDictionary.segment_by_meaning("兢兢業業"), ["兢兢", "業", "業"])
        self.assertEqual(PediaDictionary.segment_by_meaning("八面玲瓏"), ["八", "面", "玲瓏"])
        self.assertEqual(PediaDictionary.segment_by_meaning("喋喋不休"), ["喋喋", "不", "休"])
        self.assertEqual(PediaDictionary.segment_by_meaning("躊躇滿志"), ["躊躇", "滿", "志"])
        self.assertEqual(PediaDictionary.segment_by_meaning("蚍蜉撼樹"), ["蚍蜉", "撼", "樹"])
        self.assertEqual(PediaDictionary.segment_by_meaning("小巧玲瓏"), ["小", "巧", "玲瓏"])
        self.assertEqual(
            PediaDictionary.segment_by_meaning("打退堂鼓"), ["打", "退", "堂", "鼓"]
        )
        self.assertEqual(
            PediaDictionary.segment_by_meaning("胸有成竹"), ["胸", "有", "成", "竹"]
        )
        self.assertEqual(PediaDictionary.segment_by_meaning("五彩繽紛"), ["五", "彩", "繽紛"])
