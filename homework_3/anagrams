"""Тесты к задаче 2 "Anagrams". Запуск: python -m unittest -v"""

import io
import random
import unittest
from collections import Counter
from contextlib import redirect_stdout
from unittest.mock import patch

from main import group_anagrams, main, parse_words, read_words, sort_groups

README_WORDS = ["eat", "tea", "tan", "ate", "nat", "bat"]


def naive_groups(strs):
    """Независимый оракул: попарное сравнение наборов букв через Counter, без ключей."""
    groups = []
    for word in strs:
        for group in groups:
            if Counter(group[0]) == Counter(word):
                group.append(word)
                break
        else:
            groups.append([word])
    return groups


def random_words(rnd, alphabet, max_len, max_count):
    """Случайный список слов. Маленький алфавит дает много анаграмм и повторов."""
    return ["".join(rnd.choice(alphabet) for _ in range(rnd.randint(0, max_len)))
            for _ in range(rnd.randint(0, max_count))]


class TestGroupAnagrams(unittest.TestCase):

    def test_example(self):
        """Пример из условия, вывод совпадает с ним буквально"""
        result = sort_groups(group_anagrams(README_WORDS))
        self.assertEqual(result, [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]])

    def test_order_of_appearance(self):
        """Без sort_groups: группы по первому появлению ключа, слова в порядке входа"""
        result = group_anagrams(README_WORDS)
        self.assertEqual(result, [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]])

    def test_empty_list(self):
        """Граница: слов нет - групп нет"""
        self.assertEqual(group_anagrams([]), [])

    def test_one_word(self):
        """Граница: одно слово - одна группа"""
        self.assertEqual(group_anagrams(["a"]), [["a"]])

    def test_empty_string(self):
        """Граница: пустая строка - тоже слово, ее ключ ''"""
        self.assertEqual(group_anagrams([""]), [[""]])
        self.assertEqual(group_anagrams(["", "b", ""]), [["", ""], ["b"]])

    def test_all_anagrams(self):
        """Все слова - перестановки одного набора букв"""
        words = ["listen", "silent", "enlist", "tinsel", "inlets"]
        self.assertEqual(group_anagrams(words), [words])

    def test_no_anagrams(self):
        """Ни одной пары анаграмм: каждое слово в своей группе"""
        self.assertEqual(group_anagrams(["abc", "abd", "xyz"]), [["abc"], ["abd"], ["xyz"]])

    def test_duplicates(self):
        """Одинаковые слова - анаграммы друг друга и не теряются"""
        self.assertEqual(group_anagrams(["a", "b", "a", "a"]), [["a", "a", "a"], ["b"]])

    def test_same_letters_different_counts(self):
        """Те же буквы в другом количестве - не анаграммы (ключи aab и abb)"""
        self.assertEqual(group_anagrams(["aab", "abb", "bab", "aba"]),
                         [["aab", "aba"], ["abb", "bab"]])

    def test_different_lengths(self):
        """Слова разной длины не смешиваются, даже при общем наборе букв"""
        self.assertEqual(group_anagrams(["ab", "aab", "ba", "abab"]),
                         [["ab", "ba"], ["aab"], ["abab"]])

    def test_returns_same_objects(self):
        """В группы кладутся сами слова входа, а не копии или ключи"""
        words = ["tea", "eat"]
        group = group_anagrams(words)[0]
        self.assertIs(group[0], words[0])
        self.assertIs(group[1], words[1])

    def test_input_not_modified(self):
        """Входной список после вызова не меняется"""
        words = ["eat", "tea", "tan"]
        group_anagrams(words)
        self.assertEqual(words, ["eat", "tea", "tan"])

    def test_against_oracle(self):
        """Сверка с оракулом на Counter на 300 случайных списках, включая порядок групп и слов"""
        rnd = random.Random(42)
        for _ in range(300):
            words = random_words(rnd, "abc", 4, 25)
            self.assertEqual(group_anagrams(words), naive_groups(words), words)

    def test_invariants(self):
        """Каждое слово ровно в одной группе, внутри группы анаграммы, у разных групп разные наборы букв"""
        rnd = random.Random(7)
        for _ in range(200):
            words = random_words(rnd, "abcd", 5, 30)
            groups = group_anagrams(words)
            self.assertEqual(sorted(w for g in groups for w in g), sorted(words), words)
            self.assertTrue(all(g for g in groups), words)
            counters = [Counter(g[0]) for g in groups]
            for g, c in zip(groups, counters):
                self.assertTrue(all(Counter(w) == c for w in g), g)
            for i in range(len(counters)):
                for j in range(i + 1, len(counters)):
                    self.assertNotEqual(counters[i], counters[j], words)

    def test_big_input(self):
        """10 000 перемешанных слов длины 100 из 10 наборов букв"""
        rnd = random.Random(1)
        base = ["".join(rnd.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(100))
                for _ in range(10)]
        words = []
        for i in range(10_000):
            letters = list(base[i % 10])
            rnd.shuffle(letters)
            words.append("".join(letters))
        groups = group_anagrams(words)
        self.assertEqual(len(groups), len({"".join(sorted(b)) for b in base}))
        self.assertEqual(sum(len(g) for g in groups), 10_000)


class TestSortGroups(unittest.TestCase):

    def test_order(self):
        """По размеру, при равном размере - по словам"""
        self.assertEqual(sort_groups([["tea", "ate"], ["z"], ["b"]]),
                         [["b"], ["z"], ["ate", "tea"]])

    def test_empty(self):
        """Пустой ответ остается пустым"""
        self.assertEqual(sort_groups([]), [])

    def test_does_not_modify_groups(self):
        """sort_groups возвращает новые списки и не трогает исходные группы"""
        groups = [["tea", "ate"], ["b"]]
        sort_groups(groups)
        self.assertEqual(groups, [["tea", "ate"], ["b"]])


class TestReadmeExample(unittest.TestCase):

    def test_states(self):
        """Состояние groups после каждого шага совпадает с таблицей визуализации в README"""
        expected = [
            [("aet", ["eat"])],
            [("aet", ["eat", "tea"])],
            [("aet", ["eat", "tea"]), ("ant", ["tan"])],
            [("aet", ["eat", "tea", "ate"]), ("ant", ["tan"])],
            [("aet", ["eat", "tea", "ate"]), ("ant", ["tan", "nat"])],
            [("aet", ["eat", "tea", "ate"]), ("ant", ["tan", "nat"]), ("abt", ["bat"])],
        ]
        for step, state in enumerate(expected, start=1):
            # группы по первым step словам - это состояние после шага step
            groups = group_anagrams(README_WORDS[:step])
            self.assertEqual([("".join(sorted(g[0])), g) for g in groups], state, step)


class TestInput(unittest.TestCase):

    def run_main(self, lines):
        """Запускает main с подмененным вводом и возвращает напечатанное."""
        out = io.StringIO()
        with patch("builtins.input", side_effect=lines), redirect_stdout(out):
            main()
        return out.getvalue()

    def test_parse_words(self):
        """Разбор строки: нормальный ввод и мусор"""
        self.assertEqual(parse_words("eat tea tan"), ["eat", "tea", "tan"])
        self.assertEqual(parse_words("  bat   tab "), ["bat", "tab"])
        for bad in ["", "   ", "eat Tea", "eat t3a", "eat, tea", "кот ток", "café"]:
            self.assertIsNone(parse_words(bad), bad)

    def test_read_words(self):
        """read_words берет строку из input и разбирает ее"""
        cases = {
            "eat tea tan ate nat bat": README_WORDS,
            "a": ["a"],
            "": None,
            "Eat": None,
            "1 2": None,
        }
        for text, expected in cases.items():
            with patch("builtins.input", return_value=text):
                self.assertEqual(read_words("> "), expected, text)

    def test_main(self):
        """Запуск программы на примере из условия"""
        self.assertEqual(self.run_main(["eat tea tan ate nat bat"]),
                         "[['bat'], ['nat', 'tan'], ['ate', 'eat', 'tea']]\n")

    def test_main_bad_input(self):
        """Некорректный ввод: сообщение вместо исключения"""
        for lines in (["eat 42"], [""], ["Eat"]):
            self.assertTrue(self.run_main(lines).startswith("Некорректный ввод"), lines)


if __name__ == "__main__":
    unittest.main()
