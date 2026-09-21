# Домашняя работа 2. Задача 2. Validate
# Максим Царьков

import random                           # для случайных последовательностей в тестах
import unittest                         # стандартный модуль для тестов
from itertools import permutations      # полный перебор перестановок в тестах

TITLE = "Задача 2. Validate"            # заголовок, который печатается над меню

# решение

def validate_stack_sequences(pushed, popped):
    """True, если popped можно получить из pushed операциями push и pop на пустом стеке.

    Моделируем стек: кладем элементы pushed по очереди и после каждого push
    снимаем с вершины все, что совпадает с очередным элементом popped.
    """
    stack = []                          # обычный список, вершина стека - его конец
    j = 0                               # индекс элемента popped, который ждем следующим
    for x in pushed:                    # каждый элемент кладется ровно один раз
        stack.append(x)                 # push(x)
        while stack and j < len(popped) and stack[-1] == popped[j]:   # на вершине тот, кого надо снять
            stack.pop()                 # pop()
            j += 1                      # ждем следующий элемент popped
    return not stack and j == len(popped)   # все снято и снято ровно в порядке popped

def is_permutation(pushed, popped):
    """Проверка условия задачи: одинаковая длина и одинаковый набор элементов."""
    return len(pushed) == len(popped) and set(pushed) == set(popped)   # элементы уникальные, set хватает

def parse_numbers(s):
    """Разбирает строку вида '1 2 3 4 5'. None, если ввод некорректный."""
    parts = s.split()                           # режем строку по пробелам
    if not parts:                               # пустая строка, по условию длина >= 1
        return None                             # признак некорректного ввода
    for token in parts:                         # проверяем каждый элемент
        body = token[1:] if token.startswith("-") else token   # минус допустим, числа целые
        if not body.isdigit():                  # буквы, точка, двойной минус
            return None                         # признак некорректного ввода
    numbers = [int(token) for token in parts]   # переводим в числа
    if len(set(numbers)) != len(numbers):       # по условию элементы уникальные
        return None                             # повторы не принимаем
    return numbers                              # корректная последовательность

def read_numbers(prompt):
    """Читает последовательность уникальных целых через пробел. None, если ввод некорректный."""
    return parse_numbers(input(prompt))         # вся проверка живет в parse_numbers

# тексты

# текст для пункта 2
EXPLANATION = """\
Порядок push задан жестко - это pushed, свобода есть только в том, когда делать
pop. Поэтому просто повторяем работу стека и на каждом шаге решаем, снимать
элемент или нет.
Правило такое: после очередного push смотрим на вершину стека. Если там лежит
ровно тот элемент, который следующим должен появиться в popped, снимаем его
сразу и смотрим на новую вершину, пока совпадения идут. Если на вершине
другой элемент, снимать его нельзя (он бы вышел не в свою очередь), и нужный
элемент можно достать только дальнейшими push.
Почему снимать надо сразу, а не откладывать. Элементы уникальные, значит
нужный элемент встречается в pushed один раз и уже лежит на вершине. Если
отложить pop и положить сверху что-то еще, то этот элемент окажется под новым
и выйти раньше него уже не сможет, хотя в popped он идет раньше. То есть
откладывание никогда не помогает, и жадная стратегия ничего не теряет.
Если в конце стек пустой и все элементы popped пройдены, последовательность
операций нашлась - ответ True. Если что-то осталось в стеке, значит на вершине
застрял элемент, которого popped ждет позже, а нужный лежит под ним - ответ
False.
В коде стек - обычный список: append это push, pop это pop, stack[-1] это
вершина. Индекс j показывает, какой элемент popped ждем следующим. Проверка
j < len(popped) в условии while нужна, чтобы не обратиться к popped[j] за
границей списка, если popped закончилась раньше, чем стек опустел."""

# текст для пункта 3
COMPLEXITY = """\
Обозначение: n - длина pushed (она же длина popped).
Время: O(n). Внешний цикл делает ровно n операций push. Внутренний while
выглядит как вложенный цикл, но каждая его итерация - это pop, а снять
элемент можно не больше одного раза. Значит за всю работу функции pop будет
не больше n. Итого не больше 2n операций со стеком, каждая за O(1)
(append и pop с конца списка в Python работают за амортизированное O(1)).
Память: O(n). Стек в худшем случае хранит все элементы сразу, например когда
popped - это pushed в обратном порядке: сначала выполняются все n push и
только потом все pop. Кроме стека есть только индекс j.
При n до 100 000 это десятки миллисекунд."""

# пункты меню

def action_run():
    pushed = read_numbers("pushed: ")                                           # первая последовательность
    if pushed is None:                                                          # ввод не подошел
        print("Некорректный ввод: нужны уникальные целые числа через пробел")   # сообщаем причину
        return                                                                  # возвращаемся в меню
    popped = read_numbers("popped: ")                                           # вторая последовательность
    if popped is None:                                                          # ввод не подошел
        print("Некорректный ввод: нужны уникальные целые числа через пробел")   # сообщаем причину
        return                                                                  # возвращаемся в меню
    if not is_permutation(pushed, popped):                                      # нарушено условие задачи
        print("Некорректный ввод: popped должна быть перестановкой pushed")     # сообщаем причину
        return                                                                  # возвращаемся в меню
    print(f"result: {validate_stack_sequences(pushed, popped)}")                # печатаем ответ

def action_explanation():
    print(EXPLANATION)                  # выводим готовый текст

def action_complexity():
    print(COMPLEXITY)                   # выводим готовый текст

def action_visualization():
    s = input("pushed (Enter - взять 1 2 3 4 5 и popped 1 3 5 4 2): ").strip()  # можно задать свой пример
    if s == "":                                                                 # ничего не ввели
        pushed, popped = [1, 2, 3, 4, 5], [1, 3, 5, 4, 2]                       # берем пример из условия
    else:                                                                       # ввели свой пример
        pushed = parse_numbers(s)                                               # разбираем pushed
        popped = read_numbers("popped: ")                                       # и дочитываем popped
        if pushed is None or popped is None:                                    # ввели не то
            print("Некорректный ввод: нужны уникальные целые числа через пробел")   # сообщаем причину
            return                                                              # возвращаемся в меню
        if not is_permutation(pushed, popped):                                  # нарушено условие задачи
            print("Некорректный ввод: popped должна быть перестановкой pushed") # сообщаем причину
            return                                                              # возвращаемся в меню
    print()                                                                     # пустая строка перед таблицей
    print(f"{'шаг':>4} {'операция':<10} {'стек':<20} {'ждем':>6}  комментарий") # шапка таблицы
    stack, j, step = [], 0, 0                                                   # начальные значения и счетчик шагов
    print(f"{'-':>4} {'-':<10} {str(stack):<20} {popped[j]:>6}  начало, стек пустой")   # состояние до цикла
    for x in pushed:                                                            # тот же цикл, что в решении
        step += 1                                                               # пошел очередной шаг
        stack.append(x)                                                         # push(x)
        top_ok = stack[-1] == popped[j]                                         # совпала ли вершина
        note = "вершина совпала" if top_ok else f"на вершине {x}, а ждем {popped[j]}"   # поясняем шаг
        print(f"{step:>4} {f'push({x})':<10} {str(stack):<20} {popped[j]:>6}  {note}")  # состояние после push
        while stack and j < len(popped) and stack[-1] == popped[j]:             # тот же while, что в решении
            step += 1                                                           # еще один шаг
            y = stack.pop()                                                     # pop()
            j += 1                                                              # следующий элемент popped
            wait = popped[j] if j < len(popped) else "-"                        # popped могла закончиться
            print(f"{step:>4} {f'pop({y})':<10} {str(stack):<20} {wait:>6}  сняли {y}")  # состояние после pop
    if not stack:                                                               # все снято
        print("\nСтек пустой, popped пройдена целиком. Ответ: True")
    else:                                                                       # что-то застряло
        print(f"\nВ стеке остались {stack}: ждем {popped[j]}, а на вершине {stack[-1]}. Ответ: False")

def action_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)   # собираем все методы test_*
    unittest.TextTestRunner(verbosity=2).run(suite)              # запускаем и печатаем отчет

def all_pop_orders(pushed):
    """Для тестов: все последовательности pop, которые можно получить из pushed (полный перебор)."""
    result = set()                                          # сюда собираем найденные порядки
    def go(i, stack, out):                                  # i - сколько уже положили
        if i == len(pushed) and not stack:                  # все положили и все сняли
            result.add(tuple(out))                          # запоминаем порядок
            return                                          # ветка закончена
        if i < len(pushed):                                 # вариант 1: сделать push
            go(i + 1, stack + [pushed[i]], out)             # копии списков, чтобы ветки не мешали
        if stack:                                           # вариант 2: сделать pop
            go(i, stack[:-1], out + [stack[-1]])            # снимаем вершину в ответ
    go(0, [], [])                                           # старт с пустого стека
    return result                                           # множество всех возможных popped

class Tests(unittest.TestCase):

    def test_examples(self):
        """Примеры из условия"""
        self.assertTrue(validate_stack_sequences([1, 2, 3, 4, 5], [1, 3, 5, 4, 2]))   # пример 1
        self.assertFalse(validate_stack_sequences([1, 2, 3], [3, 1, 2]))              # пример 2

    def test_same_order(self):
        """popped совпадает с pushed: каждый push сразу снимается"""
        self.assertTrue(validate_stack_sequences([1, 2, 3, 4], [1, 2, 3, 4]))         # push, pop, push, pop ...

    def test_reverse_order(self):
        """popped - pushed задом наперед: сначала все push, потом все pop"""
        self.assertTrue(validate_stack_sequences([1, 2, 3, 4], [4, 3, 2, 1]))         # стек заполняется целиком

    def test_one_element(self):
        """Граница: одна операция push и одна pop"""
        self.assertTrue(validate_stack_sequences([7], [7]))                           # минимальный вход

    def test_two_elements(self):
        """Граница: из двух элементов получаются оба порядка"""
        self.assertTrue(validate_stack_sequences([1, 2], [1, 2]))                     # push, pop, push, pop
        self.assertTrue(validate_stack_sequences([1, 2], [2, 1]))                     # push, push, pop, pop

    def test_false_cases(self):
        """Нужный элемент оказывается под другим"""
        self.assertFalse(validate_stack_sequences([1, 2, 3, 4, 5], [4, 3, 5, 1, 2]))  # 1 под 2
        self.assertFalse(validate_stack_sequences([1, 2, 3, 4, 5], [4, 5, 3, 1, 2]))  # 1 под 2
        self.assertFalse(validate_stack_sequences([1, 2, 3], [3, 1, 2]))              # тот же случай, что пример 2

    def test_nontrivial_true(self):
        """Чередование: часть снимается сразу, часть копится"""
        self.assertTrue(validate_stack_sequences([1, 2, 3, 4, 5], [4, 5, 3, 2, 1]))   # 1 2 3 4 копятся
        self.assertTrue(validate_stack_sequences([1, 2, 3, 4, 5, 6], [2, 1, 4, 3, 6, 5]))   # пары меняются местами

    def test_last_pop_at_end(self):
        """Граница: popped заканчивается внутри while, индекс не выходит за границу"""
        self.assertTrue(validate_stack_sequences([1, 2, 3], [3, 2, 1]))               # j доходит до len(popped) во while

    def test_negative_and_zero(self):
        """Числа не обязательно положительные, важна только уникальность"""
        self.assertTrue(validate_stack_sequences([0, -1, 5, -7], [-1, 0, -7, 5]))     # push 0, -1, pop, pop, ...
        self.assertFalse(validate_stack_sequences([0, -1, 5, -7], [5, 0, -1, -7]))    # 0 под -1

    def test_not_permutation(self):
        """Условие нарушено: функция не падает и отвечает False"""
        self.assertFalse(validate_stack_sequences([1, 2, 3], [1, 2, 4]))              # 3 не снимется никогда
        self.assertFalse(validate_stack_sequences([1, 2, 3], [1, 2]))                 # 3 остается в стеке
        self.assertFalse(is_permutation([1, 2, 3], [1, 2, 4]))                        # проверка условия
        self.assertTrue(is_permutation([1, 2, 3], [3, 1, 2]))                         # перестановка

    def test_max_length(self):
        """Граница: n = 100 000, и хороший, и плохой ответ"""
        n = 100_000                                                             # верхняя граница из условия
        pushed = list(range(n))                                                 # 0, 1, ..., n - 1
        self.assertTrue(validate_stack_sequences(pushed, pushed[::-1]))         # стек заполняется до n
        self.assertTrue(validate_stack_sequences(pushed, pushed[:]))            # стек не больше 1
        bad = pushed[::-1]                                                      # обратный порядок
        bad[-1], bad[-2] = bad[-2], bad[-1]                                     # 0 раньше 1, а он лежит под 1
        self.assertFalse(validate_stack_sequences(pushed, bad))                 # ответ False

    def test_against_brute_force(self):
        """Сверка со всеми перестановками и полным перебором операций при n до 6"""
        for n in range(1, 7):                                           # 6! = 720 перестановок, быстро
            pushed = list(range(1, n + 1))                              # 1, 2, ..., n
            good = all_pop_orders(pushed)                               # все допустимые popped
            for popped in permutations(pushed):                         # проверяем каждую перестановку
                expected = popped in good                               # ответ перебором
                self.assertEqual(validate_stack_sequences(pushed, list(popped)), expected, popped)

    def test_random_valid(self):
        """Случайные push и pop на стеке всегда дают последовательность с ответом True"""
        rnd = random.Random(42)                                         # фиксируем seed, тест воспроизводим
        for _ in range(300):                                            # 300 случайных прогонов
            n = rnd.randint(1, 200)                                     # длина до 200
            pushed = rnd.sample(range(-1000, 1000), n)                  # уникальные числа в случайном порядке
            stack, popped, i = [], [], 0                                # моделируем стек случайно
            while len(popped) < n:                                      # пока не сняли все
                if i < n and (not stack or rnd.random() < 0.5):         # push, если есть что класть
                    stack.append(pushed[i])                             # кладем
                    i += 1                                              # следующий элемент pushed
                else:                                                   # иначе pop
                    popped.append(stack.pop())                          # снимаем в popped
            self.assertTrue(validate_stack_sequences(pushed, popped), (pushed, popped))

    def test_parse_numbers(self):
        """Разбор строки: нормальный ввод и мусор"""
        self.assertEqual(parse_numbers("1 2 3 4 5"), [1, 2, 3, 4, 5])      # пример из условия
        self.assertEqual(parse_numbers("  -3   0 7 "), [-3, 0, 7])         # лишние пробелы, минус, ноль
        self.assertIsNone(parse_numbers(""))                               # пустая строка
        self.assertIsNone(parse_numbers("1 2 2"))                          # повтор
        self.assertIsNone(parse_numbers("1 x 3"))                          # буква
        self.assertIsNone(parse_numbers("1 2.5"))                          # дробь
        self.assertIsNone(parse_numbers("--1"))                            # двойной минус

    def test_read_numbers(self):
        """Корректность ввода через read_numbers

        Настоящего ввода с клавиатуры в тестах нет, поэтому на время проверки
        закрываем имя input одноименной глобальной переменной модуля.
        """
        global input                                        # подменять будем глобальное имя
        cases = {                                           # строка ввода -> что должно вернуться
            "1 3 5 4 2": [1, 3, 5, 4, 2],                   # обычный случай
            "42": [42],                                     # один элемент
            "": None,                                       # пустая строка
            "1 1": None,                                    # повтор
            "a b": None,                                    # буквы вместо чисел
        }
        try:                                                # подмену надо снять в любом случае
            for text, expected in cases.items():            # проверяем вводы по очереди
                input = lambda prompt, s=text: s            # вместо чтения с клавиатуры отдаем s
                self.assertEqual(read_numbers("> "), expected, text)   # ответ совпал с ожидаемым
        finally:                                            # даже если проверка не прошла
            del input                                       # имя убрали, снова работает встроенный input

# меню

MENU = {
    "1": ("Запуск", action_run),                                    # ввод данных и ответ
    "2": ("Объяснение решения", action_explanation),                # описание алгоритма
    "3": ("Оценка сложности", action_complexity),                   # время и память
    "4": ("Визуализация работы алгоритма", action_visualization),   # стек по шагам
    "5": ("Тесты", action_tests),                                   # прогон тестов
}

def main():
    while True:                                     # меню показывается, пока не выбран выход
        print("\n" + TITLE)                         # заголовок задачи
        for number, (name, _) in MENU.items():      # перебираем пункты по порядку
            print(f"{number}. {name}")              # печатаем номер и название
        print("6. Выход")                           # последний пункт обрабатывается отдельно
        choice = input("Выберите пункт: ").strip()  # читаем номер пункта
        if choice == "6":                           # выбран выход
            break                                   # выходим из цикла, программа завершается
        if choice not in MENU:                      # введено что-то постороннее
            print("Такого пункта нет")              # предупреждаем
            continue                                # и показываем меню заново
        print()                                     # отступ перед выводом пункта
        MENU[choice][1]()                           # вызываем функцию выбранного пункта

if __name__ == "__main__":                          # запуск только при прямом вызове файла
    main()                                          # стартуем меню
