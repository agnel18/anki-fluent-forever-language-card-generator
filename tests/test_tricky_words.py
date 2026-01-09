#!/usr/bin/env python3
"""
Test Suite for Tricky Words in Chinese Traditional Grammar Analyzer
Tests the 10 tricky words provided by the user to ensure correct role assignment and high confidence.
"""

import pytest
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'streamlit_app'))

from languages.chinese_traditional.zh_tw_analyzer import ZhTwAnalyzer


class TestTrickyWords:
    """Test suite for 10 tricky Chinese Traditional words"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ZhTwAnalyzer()

    @pytest.fixture
    def tricky_words_data(self):
        """Data for tricky words: word, sentences, expected_roles, mock_responses"""
        return {
            "了": {
                "sentences": [
                    "我吃了飯了",  # aspect + modal
                    "我已經吃了",  # pure aspect
                    "他去了學校",  # aspect
                    "雨停了"       # change of state modal
                ],
                "expected_roles": ["aspect_particle", "aspect_particle", "aspect_particle", "modal_particle"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我吃了飯了",
                            "words": [
                                {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "了", "individual_meaning": "perfective aspect", "grammatical_role": "aspect_particle"},
                                {"word": "飯", "individual_meaning": "meal", "grammatical_role": "noun"},
                                {"word": "了", "individual_meaning": "sentence final particle", "grammatical_role": "modal_particle"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我已經吃了",
                            "words": [
                                {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                                {"word": "已經", "individual_meaning": "already", "grammatical_role": "adverb"},
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "了", "individual_meaning": "perfective aspect", "grammatical_role": "aspect_particle"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "他去了學校",
                            "words": [
                                {"word": "他", "individual_meaning": "he", "grammatical_role": "pronoun"},
                                {"word": "去", "individual_meaning": "go", "grammatical_role": "verb"},
                                {"word": "了", "individual_meaning": "perfective aspect", "grammatical_role": "aspect_particle"},
                                {"word": "學校", "individual_meaning": "school", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "雨停了",
                            "words": [
                                {"word": "雨", "individual_meaning": "rain", "grammatical_role": "noun"},
                                {"word": "停", "individual_meaning": "stop", "grammatical_role": "verb"},
                                {"word": "了", "individual_meaning": "change of state", "grammatical_role": "modal_particle"}
                            ]
                        }]
                    }
                ]
            },
            "著": {
                "sentences": [
                    "門開著",      # durative aspect
                    "他正看著書",  # progressive with 著
                    "書放著",      # state
                    "穿著衣服"     # wear (different meaning)
                ],
                "expected_roles": ["aspect_particle", "aspect_particle", "aspect_particle", "verb"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "門開著",
                            "words": [
                                {"word": "門", "individual_meaning": "door", "grammatical_role": "noun"},
                                {"word": "開", "individual_meaning": "open", "grammatical_role": "verb"},
                                {"word": "著", "individual_meaning": "durative aspect", "grammatical_role": "aspect_particle"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "他正看著書",
                            "words": [
                                {"word": "他", "individual_meaning": "he", "grammatical_role": "pronoun"},
                                {"word": "正", "individual_meaning": "just", "grammatical_role": "adverb"},
                                {"word": "看", "individual_meaning": "read", "grammatical_role": "verb"},
                                {"word": "著", "individual_meaning": "durative aspect", "grammatical_role": "aspect_particle"},
                                {"word": "書", "individual_meaning": "book", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "書放著",
                            "words": [
                                {"word": "書", "individual_meaning": "book", "grammatical_role": "noun"},
                                {"word": "放", "individual_meaning": "put", "grammatical_role": "verb"},
                                {"word": "著", "individual_meaning": "durative aspect", "grammatical_role": "aspect_particle"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "穿著衣服",
                            "words": [
                                {"word": "穿", "individual_meaning": "wear", "grammatical_role": "verb"},
                                {"word": "著", "individual_meaning": "wearing", "grammatical_role": "verb"},
                                {"word": "衣服", "individual_meaning": "clothes", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "穿著衣服", "combined_meaning": "wearing clothes", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "過": {
                "sentences": [
                    "我去過北京",  # experiential
                    "走過橋",      # cross
                    "吃過飯",      # experienced eating
                    "飛過天空"     # flew across
                ],
                "expected_roles": ["aspect_particle", "verb", "aspect_particle", "verb"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我去過北京",
                            "words": [
                                {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                                {"word": "去", "individual_meaning": "go", "grammatical_role": "verb"},
                                {"word": "過", "individual_meaning": "experiential aspect", "grammatical_role": "aspect_particle"},
                                {"word": "北京", "individual_meaning": "Beijing", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "走過橋",
                            "words": [
                                {"word": "走", "individual_meaning": "walk", "grammatical_role": "verb"},
                                {"word": "過", "individual_meaning": "cross", "grammatical_role": "verb"},
                                {"word": "橋", "individual_meaning": "bridge", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "走過橋", "combined_meaning": "walk across the bridge", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "吃過飯",
                            "words": [
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "過", "individual_meaning": "experiential aspect", "grammatical_role": "aspect_particle"},
                                {"word": "飯", "individual_meaning": "meal", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "飛過天空",
                            "words": [
                                {"word": "飛", "individual_meaning": "fly", "grammatical_role": "verb"},
                                {"word": "過", "individual_meaning": "across", "grammatical_role": "verb"},
                                {"word": "天空", "individual_meaning": "sky", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "飛過天空", "combined_meaning": "fly across the sky", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "的": {
                "sentences": [
                    "我的書",      # possession
                    "漂亮的女孩",  # attribution
                    "老師的學生",  # possession
                    "紅色的花"     # attribution
                ],
                "expected_roles": ["structural_particle", "structural_particle", "structural_particle", "structural_particle"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我的書",
                            "words": [
                                {"word": "我", "individual_meaning": "my", "grammatical_role": "pronoun"},
                                {"word": "的", "individual_meaning": "possessive particle", "grammatical_role": "structural_particle"},
                                {"word": "書", "individual_meaning": "book", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "我的書", "combined_meaning": "my book", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "漂亮的女孩",
                            "words": [
                                {"word": "漂亮", "individual_meaning": "beautiful", "grammatical_role": "adjective"},
                                {"word": "的", "individual_meaning": "attributive particle", "grammatical_role": "structural_particle"},
                                {"word": "女孩", "individual_meaning": "girl", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "漂亮的女孩", "combined_meaning": "beautiful girl", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "老師的學生",
                            "words": [
                                {"word": "老師", "individual_meaning": "teacher", "grammatical_role": "noun"},
                                {"word": "的", "individual_meaning": "possessive particle", "grammatical_role": "structural_particle"},
                                {"word": "學生", "individual_meaning": "student", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "老師的學生", "combined_meaning": "teacher's student", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "紅色的花",
                            "words": [
                                {"word": "紅色", "individual_meaning": "red", "grammatical_role": "adjective"},
                                {"word": "的", "individual_meaning": "attributive particle", "grammatical_role": "structural_particle"},
                                {"word": "花", "individual_meaning": "flower", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "紅色的花", "combined_meaning": "red flower", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "地": {
                "sentences": [
                    "慢慢地走",    # adverbial
                    "快樂地唱歌",  # adverbial
                    "仔細地看",    # adverbial
                    "輕輕地說"     # adverbial
                ],
                "expected_roles": ["structural_particle", "structural_particle", "structural_particle", "structural_particle"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "慢慢地走",
                            "words": [
                                {"word": "慢慢", "individual_meaning": "slowly", "grammatical_role": "adverb"},
                                {"word": "地", "individual_meaning": "adverbial particle", "grammatical_role": "structural_particle"},
                                {"word": "走", "individual_meaning": "walk", "grammatical_role": "verb"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "快樂地唱歌",
                            "words": [
                                {"word": "快樂", "individual_meaning": "happily", "grammatical_role": "adverb"},
                                {"word": "地", "individual_meaning": "adverbial particle", "grammatical_role": "structural_particle"},
                                {"word": "唱", "individual_meaning": "sing", "grammatical_role": "verb"},
                                {"word": "歌", "individual_meaning": "song", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "仔細地看",
                            "words": [
                                {"word": "仔細", "individual_meaning": "carefully", "grammatical_role": "adverb"},
                                {"word": "地", "individual_meaning": "adverbial particle", "grammatical_role": "structural_particle"},
                                {"word": "看", "individual_meaning": "look", "grammatical_role": "verb"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "輕輕地說",
                            "words": [
                                {"word": "輕輕", "individual_meaning": "gently", "grammatical_role": "adverb"},
                                {"word": "地", "individual_meaning": "adverbial particle", "grammatical_role": "structural_particle"},
                                {"word": "說", "individual_meaning": "say", "grammatical_role": "verb"}
                            ]
                        }]
                    }
                ]
            },
            "得": {
                "sentences": [
                    "跑得很快",    # complement
                    "吃得很飽",    # complement
                    "學得很好",    # complement
                    "說得清楚"     # complement
                ],
                "expected_roles": ["structural_particle", "structural_particle", "structural_particle", "structural_particle"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "跑得很快",
                            "words": [
                                {"word": "跑", "individual_meaning": "run", "grammatical_role": "verb"},
                                {"word": "得", "individual_meaning": "resultative particle", "grammatical_role": "structural_particle"},
                                {"word": "很", "individual_meaning": "very", "grammatical_role": "adverb"},
                                {"word": "快", "individual_meaning": "fast", "grammatical_role": "adjective"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "吃得很飽",
                            "words": [
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "得", "individual_meaning": "resultative particle", "grammatical_role": "structural_particle"},
                                {"word": "很", "individual_meaning": "very", "grammatical_role": "adverb"},
                                {"word": "飽", "individual_meaning": "full", "grammatical_role": "adjective"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "學得很好",
                            "words": [
                                {"word": "學", "individual_meaning": "study", "grammatical_role": "verb"},
                                {"word": "得", "individual_meaning": "resultative particle", "grammatical_role": "structural_particle"},
                                {"word": "很", "individual_meaning": "very", "grammatical_role": "adverb"},
                                {"word": "好", "individual_meaning": "good", "grammatical_role": "adjective"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "說得清楚",
                            "words": [
                                {"word": "說", "individual_meaning": "say", "grammatical_role": "verb"},
                                {"word": "得", "individual_meaning": "resultative particle", "grammatical_role": "structural_particle"},
                                {"word": "清楚", "individual_meaning": "clear", "grammatical_role": "adjective"}
                            ]
                        }]
                    }
                ]
            },
            "把": {
                "sentences": [
                    "把書放在桌上", # disposal
                    "把門關上",     # disposal
                    "把飯吃完",     # disposal
                    "把衣服洗乾淨"  # disposal
                ],
                "expected_roles": ["preposition", "preposition", "preposition", "preposition"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "把書放在桌上",
                            "words": [
                                {"word": "把", "individual_meaning": "disposal construction", "grammatical_role": "preposition"},
                                {"word": "書", "individual_meaning": "book", "grammatical_role": "noun"},
                                {"word": "放", "individual_meaning": "put", "grammatical_role": "verb"},
                                {"word": "在", "individual_meaning": "on", "grammatical_role": "preposition"},
                                {"word": "桌上", "individual_meaning": "table", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "放在桌上", "combined_meaning": "put on the table", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "把門關上",
                            "words": [
                                {"word": "把", "individual_meaning": "disposal construction", "grammatical_role": "preposition"},
                                {"word": "門", "individual_meaning": "door", "grammatical_role": "noun"},
                                {"word": "關", "individual_meaning": "close", "grammatical_role": "verb"},
                                {"word": "上", "individual_meaning": "up", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "關上", "combined_meaning": "close up", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "把飯吃完",
                            "words": [
                                {"word": "把", "individual_meaning": "disposal construction", "grammatical_role": "preposition"},
                                {"word": "飯", "individual_meaning": "meal", "grammatical_role": "noun"},
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "完", "individual_meaning": "finish", "grammatical_role": "verb"}
                            ],
                            "word_combinations": [
                                {"text": "吃完", "combined_meaning": "eat up", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "把衣服洗乾淨",
                            "words": [
                                {"word": "把", "individual_meaning": "disposal construction", "grammatical_role": "preposition"},
                                {"word": "衣服", "individual_meaning": "clothes", "grammatical_role": "noun"},
                                {"word": "洗", "individual_meaning": "wash", "grammatical_role": "verb"},
                                {"word": "乾淨", "individual_meaning": "clean", "grammatical_role": "adjective"}
                            ],
                            "word_combinations": [
                                {"text": "洗乾淨", "combined_meaning": "wash clean", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "個": {
                "sentences": [
                    "三個蘋果",    # classifier
                    "一個人",      # classifier
                    "五個學生",    # classifier
                    "兩個問題"     # classifier
                ],
                "expected_roles": ["measure_word", "measure_word", "measure_word", "measure_word"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "三個蘋果",
                            "words": [
                                {"word": "三", "individual_meaning": "three", "grammatical_role": "numeral"},
                                {"word": "個", "individual_meaning": "classifier", "grammatical_role": "measure_word"},
                                {"word": "蘋果", "individual_meaning": "apple", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "三個蘋果", "combined_meaning": "three apples", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "一個人",
                            "words": [
                                {"word": "一", "individual_meaning": "one", "grammatical_role": "numeral"},
                                {"word": "個", "individual_meaning": "classifier", "grammatical_role": "measure_word"},
                                {"word": "人", "individual_meaning": "person", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "一個人", "combined_meaning": "one person", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "五個學生",
                            "words": [
                                {"word": "五", "individual_meaning": "five", "grammatical_role": "numeral"},
                                {"word": "個", "individual_meaning": "classifier", "grammatical_role": "measure_word"},
                                {"word": "學生", "individual_meaning": "student", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "五個學生", "combined_meaning": "five students", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "兩個問題",
                            "words": [
                                {"word": "兩", "individual_meaning": "two", "grammatical_role": "numeral"},
                                {"word": "個", "individual_meaning": "classifier", "grammatical_role": "measure_word"},
                                {"word": "問題", "individual_meaning": "question", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "兩個問題", "combined_meaning": "two questions", "grammatical_role": "noun_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "在": {
                "sentences": [
                    "我在吃飯",    # progressive
                    "書在桌上",    # location
                    "他在跑步",    # progressive
                    "學校在這裡"   # location
                ],
                "expected_roles": ["preposition", "preposition", "preposition", "preposition"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我在吃飯",
                            "words": [
                                {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                                {"word": "在", "individual_meaning": "progressive aspect", "grammatical_role": "preposition"},
                                {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                                {"word": "飯", "individual_meaning": "meal", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "吃飯", "combined_meaning": "eat meal", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "書在桌上",
                            "words": [
                                {"word": "書", "individual_meaning": "book", "grammatical_role": "noun"},
                                {"word": "在", "individual_meaning": "at", "grammatical_role": "preposition"},
                                {"word": "桌上", "individual_meaning": "table", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "在桌上", "combined_meaning": "on the table", "grammatical_role": "prepositional_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "他在跑步",
                            "words": [
                                {"word": "他", "individual_meaning": "he", "grammatical_role": "pronoun"},
                                {"word": "在", "individual_meaning": "progressive aspect", "grammatical_role": "preposition"},
                                {"word": "跑", "individual_meaning": "run", "grammatical_role": "verb"},
                                {"word": "步", "individual_meaning": "step", "grammatical_role": "noun"}
                            ],
                            "word_combinations": [
                                {"text": "跑步", "combined_meaning": "run", "grammatical_role": "verb_phrase"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "學校在這裡",
                            "words": [
                                {"word": "學校", "individual_meaning": "school", "grammatical_role": "noun"},
                                {"word": "在", "individual_meaning": "at", "grammatical_role": "preposition"},
                                {"word": "這裡", "individual_meaning": "here", "grammatical_role": "pronoun"}
                            ],
                            "word_combinations": [
                                {"text": "在這裡", "combined_meaning": "here", "grammatical_role": "prepositional_phrase"}
                            ]
                        }]
                    }
                ]
            },
            "會": {
                "sentences": [
                    "我會說中文",  # ability
                    "明天會下雨",  # future
                    "他會游泳",    # ability
                    "我們會成功"   # future possibility
                ],
                "expected_roles": ["verb", "verb", "verb", "verb"],
                "mock_responses": [
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我會說中文",
                            "words": [
                                {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                                {"word": "會", "individual_meaning": "can", "grammatical_role": "verb"},
                                {"word": "說", "individual_meaning": "speak", "grammatical_role": "verb"},
                                {"word": "中文", "individual_meaning": "Chinese", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "明天會下雨",
                            "words": [
                                {"word": "明天", "individual_meaning": "tomorrow", "grammatical_role": "time_word"},
                                {"word": "會", "individual_meaning": "will", "grammatical_role": "verb"},
                                {"word": "下", "individual_meaning": "fall", "grammatical_role": "verb"},
                                {"word": "雨", "individual_meaning": "rain", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "他會游泳",
                            "words": [
                                {"word": "他", "individual_meaning": "he", "grammatical_role": "pronoun"},
                                {"word": "會", "individual_meaning": "can", "grammatical_role": "verb"},
                                {"word": "游", "individual_meaning": "swim", "grammatical_role": "verb"},
                                {"word": "泳", "individual_meaning": "swimming", "grammatical_role": "noun"}
                            ]
                        }]
                    },
                    {
                        "batch_results": [{
                            "sentence_index": 1,
                            "sentence": "我們會成功",
                            "words": [
                                {"word": "我們", "individual_meaning": "we", "grammatical_role": "pronoun"},
                                {"word": "會", "individual_meaning": "will", "grammatical_role": "verb"},
                                {"word": "成功", "individual_meaning": "succeed", "grammatical_role": "verb"}
                            ]
                        }]
                    }
                ]
            }
        }

    def test_tricky_words_analysis(self, analyzer, tricky_words_data):
        """Test that tricky words are analyzed correctly with high confidence"""
        for word, data in tricky_words_data.items():
            sentences = data["sentences"]
            expected_roles = data["expected_roles"]
            mock_responses = data["mock_responses"]

            for i, (sentence, expected_role, mock_response) in enumerate(zip(sentences, expected_roles, mock_responses)):
                # Parse the mock response
                results = analyzer.parse_batch_grammar_response(
                    json.dumps(mock_response),
                    [sentence],
                    "intermediate"
                )

                assert len(results) == 1
                parsed_data = results[0]

                # Find the tricky word in the parsed data
                word_found = False
                actual_role = None
                for role, elements in parsed_data.get('elements', {}).items():
                    if isinstance(elements, list):
                        for element in elements:
                            if element.get('word') == word:
                                actual_role = element.get('grammatical_role')
                                word_found = True
                                break
                    if word_found:
                        break

                assert word_found, f"Word '{word}' not found in parsed data for sentence: {sentence}"
                assert actual_role == expected_role, f"Wrong role for '{word}' in '{sentence}': expected {expected_role}, got {actual_role}"

                # PASS 2: Validate analysis
                validation_result = analyzer.validate_analysis(parsed_data, sentence)

                # Check overall validation confidence
                # For sentences with particles, expect > 0.85; for others, >= 0.7
                has_particles_in_sentence = any(role in ['aspect_particle', 'modal_particle', 'structural_particle'] 
                                             for role in parsed_data.get('elements', {}).keys())
                expected_confidence = 0.85 if has_particles_in_sentence else 0.7
                assert validation_result >= expected_confidence, f"Low validation confidence for sentence: {sentence} (score: {validation_result}, expected >= {expected_confidence})"

                print(f"✓ '{word}' in '{sentence}': role={actual_role}, validation_score={validation_result:.3f}")