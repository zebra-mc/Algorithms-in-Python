"""Тесты к задаче 3 "Создание хеш-таблицы". Запуск: python -m unittest -v"""

import io
import random
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from main import (DELETED, EMPTY, HASH_MOD, MIN_CAPACITY, HashTable, capacity_for,
                  execute, main, parse_script, read_script, slots_text,
                  string_hash)

README_SCRIPT = "a=1 i=2 q=3 b=4 ?q -i ?q y=5 i=6 c=7 d=8 ?z -z"


class Key:
    """Ключ, у которого хеш одинаковый для всех экземпляров: все попадают в одну цепочку."""

    def __init__(self, x):
        self.x = x

    def __hash__(self):
        return 7

    def __eq__(self, other):
        return isinstance(other, Key) and self.x == other.x


class StrLike:
    """Не строка, но равна строке 'a' и имеет тот же hash(): Python это разрешает, dict это учитывает."""

    def __eq__(self, other):
        return other == "a"

    def __hash__(self):
        return hash("a")


class InvariantsMixin:

    def check_invariants(self, table):
        """Счетчики сходятся с ячейками, заполнение не больше 2/3, каждый ключ находится."""
        live = sum(1 for h in table.hashes if h is not EMPTY and h is not DELETED)
        dead = sum(1 for h in table.hashes if h is DELETED)
        self.assertEqual(table.size, live)
        self.assertEqual(table.deleted, dead)
        for lst in (table.keys, table.values, table.hashes):
            self.assertEqual(len(lst), table.capacity)
        self.assertLessEqual((live + dead) * 3, table.capacity * 2)
        self.assertIn(EMPTY, table.hashes)                          # поиск всегда остановится
        self.assertGreaterEqual(table.capacity, MIN_CAPACITY)
        self.assertEqual(table.capacity & (table.capacity - 1), 0)  # степень двойки
        for i, (h, k) in enumerate(zip(table.hashes, table.keys)):
            if h is not EMPTY and h is not DELETED:
                self.assertEqual(table._find_slot(k, table.hash_func(k)), (i, True), k)
                self.assertEqual(h, table.hash_func(k))
            else:
                self.assertIsNone(k)                                # ссылки на удаленное не держим
                self.assertIsNone(table.values[i])


class TestBasic(InvariantsMixin, unittest.TestCase):

    def test_put_get_remove(self):
        """Вставка, поиск и удаление нескольких ключей"""
        t = HashTable()
        t.put("apple", 1)
        t.put("banana", 2)
        t.put("cherry", 3)
        self.assertEqual(len(t), 3)
        self.assertEqual(t.get("apple"), 1)
        self.assertEqual(t.get("banana"), 2)
        self.assertEqual(t.get("cherry"), 3)
        self.assertEqual(t.remove("banana"), 2)
        self.assertIsNone(t.get("banana"))
        self.assertEqual(len(t), 2)
        self.check_invariants(t)

    def test_update_existing_key(self):
        """Повторная вставка меняет значение, а не добавляет элемент"""
        t = HashTable()
        t.put("k", 1)
        t.put("k", 2)
        t["k"] = 3
        self.assertEqual(len(t), 1)
        self.assertEqual(t["k"], 3)
        self.check_invariants(t)

    def test_empty_table(self):
        """Граница: пустая таблица"""
        t = HashTable()
        self.assertEqual(len(t), 0)
        self.assertEqual(t.capacity, MIN_CAPACITY)
        self.assertIsNone(t.get("x"))
        self.assertEqual(t.get("x", "нет"), "нет")
        self.assertNotIn("x", t)
        self.assertEqual(list(t), [])
        self.assertEqual(repr(t), "{}")
        self.check_invariants(t)

    def test_missing_key(self):
        """get отдает default, t[k], remove и del бросают KeyError, таблица не меняется"""
        t = HashTable()
        t.put("a", 1)
        with self.assertRaises(KeyError):
            t["b"]
        with self.assertRaises(KeyError):
            t.remove("b")
        with self.assertRaises(KeyError):
            del t["b"]
        self.assertEqual(len(t), 1)
        self.assertEqual(t.deleted, 0)
        self.assertEqual(t["a"], 1)

    def test_remove_twice(self):
        """Повторное удаление бросает KeyError и не трогает счетчики"""
        t = HashTable()
        t.put("a", 1)
        t.remove("a")
        with self.assertRaises(KeyError):
            t.remove("a")
        self.assertEqual(len(t), 0)
        self.assertEqual(t.deleted, 1)
        self.check_invariants(t)

    def test_reuse_after_empty(self):
        """Таблица опустела и наполняется снова"""
        t = HashTable()
        for i in range(20):
            t.put(i, i)
        for i in range(20):
            t.remove(i)
        self.assertEqual(len(t), 0)
        for i in range(20, 30):
            t.put(i, -i)
        self.assertEqual(sorted(t.items()), [(i, -i) for i in range(20, 30)])
        self.check_invariants(t)

    def test_error_keeps_state(self):
        """После TypeError и KeyError таблица остается рабочей"""
        t = HashTable()
        with self.assertRaises(TypeError):
            t.put([1, 2], "x")
        with self.assertRaises(KeyError):
            t.remove("x")
        self.assertEqual(len(t), 0)
        t.put("x", 1)
        self.assertEqual(t["x"], 1)
        self.check_invariants(t)

    def test_independent_instances(self):
        """Две таблицы не делят списки между собой"""
        t1, t2 = HashTable(), HashTable()
        t1.put("a", 1)
        self.assertNotIn("a", t2)
        t2.put("a", 2)
        self.assertEqual(t1["a"], 1)
        self.assertIsNot(t1.keys, t2.keys)

    def test_iteration_and_repr(self):
        """Обход, items и repr идут в порядке ячеек"""
        t = HashTable(string_hash)
        t.put("a", 1)
        t.put("b", 2)
        self.assertEqual(list(t), ["a", "b"])               # 'a' в ячейке 1, 'b' в ячейке 2
        self.assertEqual(list(t.items()), [("a", 1), ("b", 2)])
        self.assertEqual(repr(t), "{'a': 1, 'b': 2}")
        self.assertEqual(len(t), 2)


class TestHash(unittest.TestCase):

    def test_string_hash(self):
        """Известные значения полиномиального хеша, порядок символов важен"""
        self.assertEqual(string_hash(""), 0)
        self.assertEqual(string_hash("a"), 97)
        self.assertEqual(string_hash("ab"), 97 * 31 + 98)
        self.assertNotEqual(string_hash("ab"), string_hash("ba"))
        self.assertLess(string_hash("x" * 1000), HASH_MOD)

    def test_string_hash_only_str(self):
        """string_hash отвергает не-строки и подклассы str, таблица на нем - тоже"""
        class MyStr(str):
            pass
        for bad in (1, ("a", "b"), ["a"], StrLike(), MyStr("a")):
            with self.assertRaises(TypeError, msg=repr(bad)):
                string_hash(bad)
        t = HashTable(string_hash)
        with self.assertRaises(TypeError):
            t.put(StrLike(), 1)
        self.assertEqual(len(t), 0)

    def test_default_hash_func(self):
        """По умолчанию ключи хешируются встроенным hash()"""
        t = HashTable()
        self.assertIs(t.hash_func, hash)
        t.put("a", 1)
        self.assertEqual(t.hashes[t._find_slot("a", hash("a"))[0]], hash("a"))

    def test_capacity_for(self):
        """Наименьшая степень двойки (не меньше 8), занятая не больше чем наполовину"""
        self.assertEqual(capacity_for(0), 8)
        self.assertEqual(capacity_for(4), 8)                # 4 элемента - ровно половина
        self.assertEqual(capacity_for(5), 16)
        self.assertEqual(capacity_for(6), 16)
        self.assertEqual(capacity_for(1000), 2048)


class TestCollisions(InvariantsMixin, unittest.TestCase):

    def test_same_home_slot(self):
        """a, i, q при 8 ячейках попадают в ячейку 1 и ложатся подряд"""
        for key in "aiq":
            self.assertEqual(string_hash(key) % 8, 1, key)
        t = HashTable(string_hash)
        for n, key in enumerate("aiq"):
            t.put(key, n)
        self.assertEqual(t.keys[1:4], ["a", "i", "q"])
        for n, key in enumerate("aiq"):
            self.assertEqual(t[key], n)
        self.check_invariants(t)

    def test_delete_in_middle_of_chain(self):
        """Удалили середину цепочки: ключ за ней все равно находится"""
        t = HashTable(string_hash)
        for key in "aiq":
            t.put(key, key)
        t.remove("i")
        self.assertIs(t.hashes[2], DELETED)
        self.assertEqual(t.get("q"), "q")                   # с EMPTY вместо метки не нашелся бы
        self.assertNotIn("i", t)
        self.check_invariants(t)

    def test_reuse_deleted_slot(self):
        """Новый ключ занимает первую удаленную ячейку на пути"""
        t = HashTable(string_hash)
        for key in "aiq":
            t.put(key, key)
        t.remove("i")
        t.put("y", "y")                                     # у 'y' тоже дом 1
        self.assertEqual(t.keys[2], "y")
        self.assertEqual(t.deleted, 0)
        self.check_invariants(t)

    def test_no_duplicate_after_delete(self):
        """Ключ стоит за удаленной ячейкой: вставка обновляет его, а не кладет копию в метку"""
        t = HashTable(string_hash)
        for key in "aiq":
            t.put(key, 0)
        t.remove("i")
        t.put("q", 5)
        self.assertEqual(t.keys.count("q"), 1)
        self.assertIs(t.hashes[2], DELETED)                   # метка осталась на месте
        self.assertEqual(t["q"], 5)
        self.check_invariants(t)

    def test_wraparound(self):
        """Цепочка переходит через конец массива в начало"""
        t = HashTable()
        for key in (7, 15, 23):                             # у всех дом 7 при 8 ячейках
            t.put(key, key)
        self.assertEqual((t.keys[7], t.keys[0], t.keys[1]), (7, 15, 23))
        t.remove(15)
        self.assertEqual(t[23], 23)
        self.check_invariants(t)

    def test_all_keys_same_hash(self):
        """Худший случай: 50 ключей с одним хешем, сравнение идет по ==, а не только по хешу"""
        t = HashTable()
        for x in range(50):
            t.put(Key(x), x)
        for x in range(50):
            self.assertEqual(t[Key(x)], x)                  # новый объект, но равный
        for x in range(0, 50, 2):
            t.remove(Key(x))
        for x in range(50):
            self.assertEqual(Key(x) in t, x % 2 == 1, x)
        self.check_invariants(t)


class TestResize(InvariantsMixin, unittest.TestCase):

    def test_resize_moment(self):
        """При 8 ячейках пятый элемент помещается (15 <= 16), шестой вызывает рост (18 > 16)"""
        t = HashTable()
        for i in range(5):
            t.put(i, i)
        self.assertEqual(t.capacity, 8)
        t.put(5, 5)
        self.assertEqual(t.capacity, 16)
        self.check_invariants(t)

    def test_update_does_not_resize(self):
        """Замена значения в заполненной на 2/3 таблице не перестраивает ее"""
        t = HashTable()
        for i in range(5):
            t.put(i, i)
        old_keys = t.keys
        t.put(3, "new")
        self.assertIs(t.keys, old_keys)

    def test_tombstone_counts_in_load(self):
        """Удаленные ячейки учитываются в заполнении: рост без сжатия, емкость та же"""
        t = HashTable()
        for i in range(5):
            t.put(i, i)
        t.remove(0)
        t.remove(1)                                         # size 3, deleted 2
        t.put(100, 100)                                     # дом 4 занят, место - свободная ячейка 5
        self.assertEqual(t.capacity, 8)                     # capacity_for(4) = 8
        self.assertEqual(t.deleted, 0)                      # перестройка убрала метки
        self.check_invariants(t)

    def test_grow(self):
        """1000 вставок: емкость удваивается 8 -> 2048, значения не теряются"""
        t = HashTable()
        capacities = [t.capacity]
        for i in range(1000):
            t.put(i, i * i)
            if t.capacity != capacities[-1]:
                capacities.append(t.capacity)
        self.assertEqual(capacities, [8, 16, 32, 64, 128, 256, 512, 1024, 2048])
        for i in range(1000):
            self.assertEqual(t[i], i * i)
        self.check_invariants(t)

    def test_shrink(self):
        """Удаление 999 из 1000 элементов: таблица сжимается до 8, заполнение в пределах порогов"""
        t = HashTable()
        for i in range(1000):
            t.put(i, str(i))
        for i in range(999):
            t.remove(i)
            self.assertLessEqual((t.size + t.deleted) * 3, t.capacity * 2)
            self.assertTrue(t.capacity == MIN_CAPACITY or t.size * 8 >= t.capacity)
        self.assertEqual(len(t), 1)
        self.assertEqual(t.capacity, MIN_CAPACITY)
        self.assertEqual(t[999], "999")
        self.check_invariants(t)

    def test_tombstones_do_not_clog(self):
        """Вставка и удаление новых ключей по кругу: метки не забивают таблицу и не раздувают ее"""
        t = HashTable()
        for i in range(10_000):
            t.put(i, i)
            t.remove(i)
        self.assertEqual(len(t), 0)
        self.assertEqual(t.capacity, MIN_CAPACITY)
        self.check_invariants(t)


class TestKeys(InvariantsMixin, unittest.TestCase):

    def test_falsy_keys_and_values(self):
        """None, 0 и пустая строка - обычные ключи и значения"""
        t = HashTable()
        t.put(None, "none")
        t.put(0, None)
        t.put("", 0)
        self.assertEqual(len(t), 3)
        self.assertEqual(t[None], "none")
        self.assertIsNone(t.get(0, "нет"))                  # значение None, а не отсутствие ключа
        self.assertIn(0, t)
        self.assertEqual(t[""], 0)
        t.remove(None)
        self.assertNotIn(None, t)
        self.check_invariants(t)

    def test_equal_keys_like_dict(self):
        """1, 1.0 и True - один ключ, как в dict"""
        t, d = HashTable(), {}
        for key, value in ((1, "int"), (1.0, "float"), (True, "bool")):
            t.put(key, value)
            d[key] = value
        self.assertEqual(list(t.items()), list(d.items()))
        self.assertIs(type(next(iter(t))), int)             # как в dict, остается первый ключ

    def test_mixed_keys(self):
        """Ключи разных типов, "1" и 1 - разные ключи"""
        t = HashTable()
        keys = [-1, -2, -10 ** 20, (1, 2), (2, 1), "1", 1, 2.5, ("a", None)]
        for n, key in enumerate(keys):
            t.put(key, n)
        self.assertEqual(len(t), len(keys))                 # "1" и 1 - разные ключи
        for n, key in enumerate(keys):
            self.assertEqual(t[key], n)
        self.check_invariants(t)

    def test_unhashable_key(self):
        """Нехешируемый ключ: TypeError, таблица не меняется"""
        t = HashTable()
        with self.assertRaises(TypeError):
            t.put([1, 2], "x")
        with self.assertRaises(TypeError):
            t.get({})
        self.assertEqual(len(t), 0)

    def test_sentinel_keys(self):
        """Служебные метки EMPTY и DELETED - тоже обычные ключи: состояние ячейки лежит в hashes"""
        t = HashTable()
        t.put(EMPTY, "e")
        t.put(DELETED, "d")
        self.assertEqual(len(t), 2)
        self.assertEqual(t[EMPTY], "e")
        self.assertIn(DELETED, t)
        self.assertEqual(t.remove(EMPTY), "e")
        self.assertNotIn(EMPTY, t)
        self.assertEqual(dict(t.items()), {DELETED: "d"})
        self.check_invariants(t)

    def test_equal_across_types(self):
        """Объект, равный строке, - тот же ключ, что и строка, как в dict"""
        t, d = HashTable(), {}
        t.put("a", 1)
        d["a"] = 1
        self.assertEqual(t[StrLike()], d[StrLike()])
        t.put(StrLike(), 2)
        d[StrLike()] = 2
        self.assertEqual(len(t), len(d))
        self.assertEqual(list(t.items()), list(d.items()))
        self.check_invariants(t)

    def test_nan_key(self):
        """NaN не равен сам себе, но тот же объект находится по is, как в dict"""
        nan = float("nan")
        t = HashTable()
        t.put(nan, "value")
        t.put(nan, "again")
        self.assertEqual(len(t), 1)
        self.assertEqual(t[nan], "again")


class TestOracle(InvariantsMixin, unittest.TestCase):

    def run_scenarios(self, make_table, pool, seed):
        """200 случайных сценариев до 300 операций, после каждой операции сверка с dict."""
        rnd = random.Random(seed)
        for _ in range(200):
            t, model = make_table(), {}
            for _ in range(rnd.randint(0, 300)):
                key = rnd.choice(pool)                      # маленький пул - много совпадений и удалений
                r = rnd.random()
                if r < 0.45:
                    value = rnd.randint(0, 100)
                    t.put(key, value)
                    model[key] = value
                elif r < 0.75:
                    if key in model:
                        self.assertEqual(t.remove(key), model.pop(key))
                    else:
                        with self.assertRaises(KeyError):
                            t.remove(key)
                else:
                    self.assertEqual(t.get(key, "нет"), model.get(key, "нет"))
                self.assertEqual(len(t), len(model))
            self.assertEqual(dict(t.items()), model)
            self.check_invariants(t)

    def test_against_oracle(self):
        """Сверка с dict (эталон, только в тестах) на ключах разных типов"""
        pool = (list(range(-15, 15)) + [f"s{i}" for i in range(15)]
                + [None, (1, 2), Key(1), Key(2), EMPTY, DELETED, 1.0, True, StrLike(), "a"])
        self.run_scenarios(HashTable, pool, 42)

    def test_against_oracle_strings(self):
        """Сверка с dict для таблицы на string_hash; однобуквенные ключи дают много коллизий"""
        pool = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["ab", "ba", ""]
        self.run_scenarios(lambda: HashTable(string_hash), pool, 43)

    def test_big_input(self):
        """100 000 строковых ключей: вставка, поиск, удаление половины"""
        n = 100_000
        t = HashTable()
        for i in range(n):
            t.put(f"key{i}", i)
        self.assertEqual(len(t), n)
        for i in range(n):
            self.assertEqual(t[f"key{i}"], i)
        for i in range(0, n, 2):
            t.remove(f"key{i}")
        self.assertEqual(len(t), n // 2)
        for i in range(n):
            self.assertEqual(f"key{i}" in t, i % 2 == 1)
        self.check_invariants(t)


class TestReadmeExample(unittest.TestCase):

    def test_states(self):
        """Состояния ячеек после каждого шага совпадают с визуализацией в README"""
        expected = [
            "0:. 1:a 2:. 3:. 4:. 5:. 6:. 7:.",
            "0:. 1:a 2:i 3:. 4:. 5:. 6:. 7:.",
            "0:. 1:a 2:i 3:q 4:. 5:. 6:. 7:.",
            "0:. 1:a 2:i 3:q 4:b 5:. 6:. 7:.",
            "0:. 1:a 2:i 3:q 4:b 5:. 6:. 7:.",
            "0:. 1:a 2:- 3:q 4:b 5:. 6:. 7:.",
            "0:. 1:a 2:- 3:q 4:b 5:. 6:. 7:.",
            "0:. 1:a 2:y 3:q 4:b 5:. 6:. 7:.",
            "0:. 1:a 2:y 3:q 4:b 5:i 6:. 7:.",
            "0:. 1:a 2:q 3:b 4:c 5:. 6:. 7:. 8:. 9:y 10:i 11:. 12:. 13:. 14:. 15:.",
            "0:. 1:a 2:q 3:b 4:c 5:d 6:. 7:. 8:. 9:y 10:i 11:. 12:. 13:. 14:. 15:.",
            "0:. 1:a 2:q 3:b 4:c 5:d 6:. 7:. 8:. 9:y 10:i 11:. 12:. 13:. 14:. 15:.",
            "0:. 1:a 2:q 3:b 4:c 5:d 6:. 7:. 8:. 9:y 10:i 11:. 12:. 13:. 14:. 15:.",
        ]
        commands = parse_script(README_SCRIPT)
        self.assertEqual(len(commands), len(expected))
        t = HashTable(string_hash)
        for command, state in zip(commands, expected):
            execute(t, [command])
            self.assertEqual(slots_text(t), state, command)

    def test_output(self):
        """Строки вывода и итоговая таблица для сценария из README"""
        t = HashTable(string_hash)
        lines = execute(t, parse_script(README_SCRIPT))
        self.assertEqual(lines[4], "?q: 3")
        self.assertEqual(lines[5], "-i: удален, значение было 2")
        self.assertEqual(lines[8], "i=6: вставлен")         # после удаления i - снова новый ключ
        self.assertEqual(lines[11], "?z: нет такого ключа")
        self.assertEqual(lines[12], "-z: нет такого ключа")
        self.assertEqual(dict(t.items()),
                         {"a": "1", "q": "3", "b": "4", "c": "7", "d": "8", "y": "5", "i": "6"})


class TestInput(unittest.TestCase):

    def run_main(self, lines):
        """Запускает main с подмененным вводом и возвращает напечатанное."""
        out = io.StringIO()
        with patch("builtins.input", side_effect=lines), redirect_stdout(out):
            main()
        return out.getvalue()

    def test_parse_script(self):
        """Разбор строки: нормальный ввод и мусор"""
        self.assertEqual(parse_script("a=1 ?a -a"),
                         [("put", "a", "1"), ("get", "a", None), ("del", "a", None)])
        self.assertEqual(parse_script("  k=v=w  "), [("put", "k", "v=w")])   # режем по первому '='
        self.assertEqual(parse_script("x="), [("put", "x", "")])
        self.assertEqual(parse_script("-a=1"), [("del", "a=1", None)])
        for bad in ("", "   ", "abc", "a=1 ?", "-", "=5"):
            self.assertIsNone(parse_script(bad), bad)

    def test_read_script(self):
        """read_script берет строку из input и разбирает ее"""
        cases = {
            "a=1 ?a": [("put", "a", "1"), ("get", "a", None)],
            "-b": [("del", "b", None)],
            "": None,
            "a=1 b": None,
        }
        for text, expected in cases.items():
            with patch("builtins.input", return_value=text):
                self.assertEqual(read_script("> "), expected, text)

    def test_execute(self):
        """Каждая команда дает строку с результатом"""
        t = HashTable()
        lines = execute(t, parse_script("a=1 b=2 a=3 ?a ?z -b -b"))
        self.assertEqual(lines, ["a=1: вставлен", "b=2: вставлен", "a=3: значение заменено",
                                 "?a: 3", "?z: нет такого ключа",
                                 "-b: удален, значение было 2", "-b: нет такого ключа"])
        self.assertEqual(dict(t.items()), {"a": "3"})

    def test_main(self):
        """Запуск программы на примере из README"""
        self.assertEqual(self.run_main(["a=1 b=2 a=3 ?a ?z -b"]),
                         "a=1: вставлен\n"
                         "b=2: вставлен\n"
                         "a=3: значение заменено\n"
                         "?a: 3\n"
                         "?z: нет такого ключа\n"
                         "-b: удален, значение было 2\n"
                         "Таблица: {'a': '3'}\n"
                         "Элементов: 1, ячеек: 8\n"
                         "Ячейки: 0:. 1:a 2:- 3:. 4:. 5:. 6:. 7:.\n")

    def test_main_bad_input(self):
        """Некорректный ввод: сообщение вместо исключения"""
        for lines in (["abc"], [""], ["a=1 ?"]):
            self.assertTrue(self.run_main(lines).startswith("Некорректный ввод"), lines)


if __name__ == "__main__":
    unittest.main()
