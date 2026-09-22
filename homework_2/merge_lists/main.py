# Домашняя работа 2. Задача 3. Merge lists
# Максим Царьков

import random                           # для случайных списков в тестах
import unittest                         # стандартный модуль для тестов

TITLE = "Задача 3. Merge lists"     # заголовок, который печатается над меню

# решение

class ListNode:
    """Узел односвязного списка: значение и ссылка на следующий узел."""

    def __init__(self, val=0, next=None):
        self.val = val                  # значение, которое хранит узел
        self.next = next                # следующий узел или None, если это конец

def merge_with_dummy(list1, list2):
    """list1, list2 - головы отсортированных списков. Возвращает голову слитого списка.

    Способ с фиктивным элементом. Заводим пустой узел dummy, и все узлы ответа,
    включая самый первый, цепляем за хвост tail одинаково. Ответ - dummy.next.
    """
    dummy = ListNode()                  # фиктивный узел, в ответ не попадает
    tail = dummy                        # последний узел уже собранной части
    while list1 is not None and list2 is not None:  # пока в обоих списках есть узлы
        if list1.val <= list2.val:      # при равенстве берем из list1, порядок равных сохраняется
            tail.next = list1           # цепляем узел из list1
            list1 = list1.next          # и сдвигаемся в list1
        else:                           # в list2 значение меньше
            tail.next = list2           # цепляем узел из list2
            list2 = list2.next          # и сдвигаемся в list2
        tail = tail.next                # хвост переезжает на прицепленный узел
    tail.next = list1 if list1 is not None else list2   # остаток уже отсортирован, цепляем целиком
    return dummy.next                   # настоящая голова стоит сразу за фиктивным узлом

def merge_without_dummy(list1, list2):
    """list1, list2 - головы отсортированных списков. Возвращает голову слитого списка.

    Способ без фиктивного элемента. Голову ответа выбираем отдельно до цикла,
    для этого сначала отсекаем пустые списки. Дальше все как в первом способе.
    """
    if list1 is None:                   # первый список пустой
        return list2                    # ответ - второй список как есть
    if list2 is None:                   # второй список пустой
        return list1                    # ответ - первый список как есть
    if list1.val <= list2.val:          # голова ответа - меньший из первых узлов
        head = list1                    # голова из list1
        list1 = list1.next              # и сдвигаемся в list1
    else:                               # в list2 первое значение меньше
        head = list2                    # голова из list2
        list2 = list2.next              # и сдвигаемся в list2
    tail = head                         # пока собранная часть - одна голова
    while list1 is not None and list2 is not None:  # тот же цикл, что в первом способе
        if list1.val <= list2.val:      # при равенстве берем из list1
            tail.next = list1           # цепляем узел из list1
            list1 = list1.next          # и сдвигаемся в list1
        else:                           # в list2 значение меньше
            tail.next = list2           # цепляем узел из list2
            list2 = list2.next          # и сдвигаемся в list2
        tail = tail.next                # хвост переезжает на прицепленный узел
    tail.next = list1 if list1 is not None else list2   # остаток цепляем целиком
    return head                         # голову запомнили еще до цикла

def build_list(values):
    """Из обычного списка Python делает односвязный. Возвращает голову или None."""
    head = None                         # пустой список
    for x in reversed(values):          # идем с конца, чтобы добавлять узлы в начало
        head = ListNode(x, head)        # новый узел становится головой
    return head

def to_values(head):
    """Из односвязного списка делает обычный список Python."""
    values = []                         # сюда складываем значения по порядку
    while head is not None:             # пока не дошли до конца
        values.append(head.val)         # запоминаем значение
        head = head.next                # переходим к следующему узлу
    return values

def merge_values(merge, a, b):
    """Строит списки из a и b, сливает функцией merge, возвращает значения ответа."""
    return to_values(merge(build_list(a), build_list(b)))   # на каждый вызов свои узлы

def parse_sorted(s):
    """Разбирает строку вида '1 2 4'. None, если ввод некорректный.

    Пустая строка допустима - это пустой список.
    """
    values = []                                 # разобранные числа
    for token in s.split():                     # режем строку по пробелам
        body = token[1:] if token.startswith("-") else token   # минус допустим
        if not body.isdigit():                  # буквы, точка, двойной минус
            return None                         # признак некорректного ввода
        values.append(int(token))               # число подошло
    for i in range(len(values) - 1):            # проверяем соседние пары
        if values[i] > values[i + 1]:           # список не отсортирован
            return None                         # признак некорректного ввода
    return values                               # корректный отсортированный список

def read_sorted(prompt):
    """Читает отсортированный список целых через пробел. None, если ввод некорректный."""
    return parse_sorted(input(prompt))          # вся проверка живет в parse_sorted

# тексты

# текст для пункта 2
EXPLANATION = """\
Оба списка уже отсортированы, поэтому самый маленький элемент ответа - это
меньший из двух первых узлов. Держим по указателю на текущий узел в каждом
списке, сравниваем их значения, меньший узел цепляем в конец ответа и
сдвигаем указатель в том списке, откуда его взяли. Оставшиеся части списков
по-прежнему отсортированы, поэтому на следующем шаге рассуждение то же самое.
Когда один из списков кончился, все узлы другого не меньше уже взятых и идут
по порядку. Значит остаток цепляется целиком одной операцией, без цикла.
Новые узлы не создаются: ответ собирается из узлов исходных списков, меняются
только ссылки next. При равных значениях берем узел из list1 (сравнение <=),
поэтому равные элементы идут в том порядке, в каком стояли.
Два способа отличаются только тем, как появляется голова ответа.
С фиктивным элементом заводим пустой узел dummy и ставим на него tail. Первый
узел ответа цепляется к dummy.next так же, как все остальные, поэтому ни
пустые списки, ни выбор головы отдельно разбирать не надо. Возвращаем dummy.next.
Без фиктивного элемента сначала отсекаем пустые списки: если один пуст, ответ -
другой. Потом выбираем голову - меньший из первых узлов - и ставим на нее tail.
Дальше тот же цикл, а возвращаем запомненную голову head. Кода больше, зато
лишний узел не создается."""

# текст для пункта 3
COMPLEXITY = """\
Обозначения: n - длина list1, m - длина list2.
Время: O(n + m). На каждой итерации цикла к ответу цепляется ровно один узел и
один из указателей сдвигается на шаг, поэтому итераций не больше n + m.
Остаток цепляется одним присваиванием, это O(1). Во втором способе добавляются
только проверки до цикла, тоже O(1).
Память: O(1) дополнительно в обоих способах. Ответ собирается из уже
существующих узлов, новых не создается. Используются несколько указателей
(tail, head) и в первом способе один фиктивный узел, их число от n и m не
зависит. Сами списки занимают O(n + m), но это память под входные данные.
Рекурсии нет, поэтому и стек не растет с длиной списков."""

# пункты меню

def action_run():
    a = read_sorted("list1 через пробел по неубыванию (Enter - пустой список): ")   # первый список
    if a is None:                                                                   # ввод не подошел
        print("Некорректный ввод: нужны целые числа через пробел по неубыванию")    # сообщаем причину
        return                                                                      # возвращаемся в меню
    b = read_sorted("list2 через пробел по неубыванию (Enter - пустой список): ")   # второй список
    if b is None:                                                                   # ввод не подошел
        print("Некорректный ввод: нужны целые числа через пробел по неубыванию")    # сообщаем причину
        return                                                                      # возвращаемся в меню
    print("С фиктивным элементом:  ", merge_values(merge_with_dummy, a, b))         # первый способ
    print("Без фиктивного элемента:", merge_values(merge_without_dummy, a, b))      # второй способ

def action_explanation():
    print(EXPLANATION)                  # выводим готовый текст

def action_complexity():
    print(COMPLEXITY)                   # выводим готовый текст

def show(values):
    """Список значений в виде строки для таблицы."""
    return " ".join(map(str, values)) if values else "пусто"   # пустой список подписываем словом

def action_visualization():
    s1 = input("list1 через пробел (Enter - взять 1 4 5 9): ").strip()      # можно задать свой пример
    s2 = input("list2 через пробел (Enter - взять 2 3 4 10 12): ").strip()  # и для второго списка
    a = [1, 4, 5, 9] if s1 == "" else parse_sorted(s1)                      # пустой ввод - пример по умолчанию
    b = [2, 3, 4, 10, 12] if s2 == "" else parse_sorted(s2)                 # то же для второго
    if a is None or b is None:                                              # ввели не то
        print("Некорректный ввод: нужны целые числа через пробел по неубыванию")   # сообщаем причину
        return                                                              # возвращаемся в меню
    list1, list2 = build_list(a), build_list(b)                             # строим связные списки
    dummy = ListNode()                                                      # то же, что в решении
    tail = dummy                                                            # хвост стоит на dummy
    merged = []                                                             # собранные значения, только для печати
    print()                                                                 # пустая строка перед таблицей
    print(f"{'шаг':>4}  {'list1':<14}{'list2':<16}{'собрано':<26}комментарий")   # шапка таблицы
    print(f"{'-':>4}  {show(a):<14}{show(b):<16}{show(merged):<26}начало, tail стоит на dummy")
    step = 0                                                                # счетчик шагов
    while list1 is not None and list2 is not None:                          # тот же цикл, что в решении
        step += 1                                                           # пошел очередной шаг
        if list1.val <= list2.val:                                          # берем из list1
            note = f"{list1.val} <= {list2.val}, цепляем {list1.val} из list1"
            tail.next = list1                                               # цепляем узел
            list1 = list1.next                                              # сдвигаемся в list1
        else:                                                               # берем из list2
            note = f"{list1.val} > {list2.val}, цепляем {list2.val} из list2"
            tail.next = list2                                               # цепляем узел
            list2 = list2.next                                              # сдвигаемся в list2
        tail = tail.next                                                    # хвост на новый узел
        merged.append(tail.val)                                             # запоминаем для печати
        print(f"{step:>4}  {show(to_values(list1)):<14}{show(to_values(list2)):<16}"
              f"{show(merged):<26}{note}")                                  # состояние после шага
    if list1 is not None:                                                   # остался list1
        note = "list2 кончился, остаток list1 цепляем целиком"
    elif list2 is not None:                                                 # остался list2
        note = "list1 кончился, остаток list2 цепляем целиком"
    else:                                                                   # оба пустые с самого начала
        note = "оба списка пустые, цеплять нечего"
    tail.next = list1 if list1 is not None else list2                       # то же присваивание, что в решении
    print(f"{step + 1:>4}  {show(to_values(list1)):<14}{show(to_values(list2)):<16}"
          f"{show(to_values(dummy.next)):<26}{note}")                       # последняя строка таблицы
    print(f"\nОтвет: dummy.next -> {show(to_values(dummy.next))}")          # ответ первым способом
    print("Без фиктивного элемента шаги те же, только первый взятый узел сразу")
    print("становится head, а не цепляется к dummy.next. Ответ:",
          show(merge_values(merge_without_dummy, a, b)))                    # второй способ для сверки

def action_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)   # собираем все методы test_*
    unittest.TextTestRunner(verbosity=2).run(suite)              # запускаем и печатаем отчет

class Tests(unittest.TestCase):

    def test_examples(self):
        """Пример из условия, оба способа"""
        for merge in (merge_with_dummy, merge_without_dummy):                   # проверяем оба способа
            self.assertEqual(merge_values(merge, [1, 2, 4], [1, 3, 4]),
                             [1, 1, 2, 3, 4, 4], merge.__name__)                # ответ из условия

    def test_empty(self):
        """Граница: один или оба списка пустые"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [], []), [], merge.__name__)           # оба пустые
            self.assertEqual(merge_values(merge, [], [0]), [0], merge.__name__)         # пустой первый
            self.assertEqual(merge_values(merge, [1, 2], []), [1, 2], merge.__name__)   # пустой второй

    def test_one_element(self):
        """Граница: по одному узлу, голова берется из любого списка"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [5], [3]), [3, 5], merge.__name__)     # голова из list2
            self.assertEqual(merge_values(merge, [3], [5]), [3, 5], merge.__name__)     # голова из list1

    def test_duplicates(self):
        """Повторы внутри списков и между ними"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [7, 7, 7], [7, 7]),
                             [7, 7, 7, 7, 7], merge.__name__)                   # все значения одинаковые
            self.assertEqual(merge_values(merge, [1, 1, 3], [1, 3, 3]),
                             [1, 1, 1, 3, 3, 3], merge.__name__)                # повторы вперемешку

    def test_negative(self):
        """Отрицательные числа и ноль"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [-10, -3, 0, 2], [-5, -3, 1]),
                             [-10, -5, -3, -3, 0, 1, 2], merge.__name__)

    def test_no_overlap(self):
        """Все элементы одного списка меньше всех элементов другого"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [1, 2, 3], [4, 5, 6]),
                             [1, 2, 3, 4, 5, 6], merge.__name__)                # остаток - весь list2
            self.assertEqual(merge_values(merge, [4, 5, 6], [1, 2, 3]),
                             [1, 2, 3, 4, 5, 6], merge.__name__)                # остаток - весь list1

    def test_long_tail(self):
        """Списки разной длины, длинный остаток цепляется целиком"""
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, [2], [1, 3, 5, 7, 9]),
                             [1, 2, 3, 5, 7, 9], merge.__name__)

    def test_nodes_reused(self):
        """Ответ собран из исходных узлов, новых узлов нет и ни один не потерян"""
        for merge in (merge_with_dummy, merge_without_dummy):
            list1, list2 = build_list([1, 4, 6]), build_list([2, 3, 5])        # исходные списки
            before = set()                                                      # id всех исходных узлов
            for node in (list1, list2):                                         # обходим оба списка
                while node is not None:
                    before.add(id(node))
                    node = node.next
            after = set()                                                       # id узлов ответа
            node = merge(list1, list2)
            while node is not None:
                after.add(id(node))
                node = node.next
            self.assertEqual(before, after, merge.__name__)                     # множества обязаны совпасть

    def test_stable(self):
        """При равных значениях первым идет узел из list1"""
        for merge in (merge_with_dummy, merge_without_dummy):
            list1, list2 = build_list([1, 2]), build_list([1, 2])              # одинаковые значения
            one, two = list1, list1.next                                        # узлы list1
            head = merge(list1, list2)
            self.assertIs(head, one, merge.__name__)                            # голова - единица из list1
            self.assertIs(head.next.next, two, merge.__name__)                  # двойка из list1 раньше двойки из list2

    def test_long_lists(self):
        """Длинные списки: рекурсии нет, стек не переполняется"""
        a = list(range(0, 200000, 2))                                           # 100000 четных
        b = list(range(1, 200000, 2))                                           # 100000 нечетных
        for merge in (merge_with_dummy, merge_without_dummy):
            self.assertEqual(merge_values(merge, a, b), list(range(200000)), merge.__name__)

    def test_against_sorted(self):
        """Сверка с sorted на случайных списках"""
        rnd = random.Random(42)                                 # фиксируем seed, тест воспроизводим
        for _ in range(300):                                    # 300 случайных пар списков
            a = sorted(rnd.randint(-20, 20) for _ in range(rnd.randint(0, 15)))    # маленький диапазон, много повторов
            b = sorted(rnd.randint(-20, 20) for _ in range(rnd.randint(0, 15)))
            expected = sorted(a + b)                            # эталонный ответ
            for merge in (merge_with_dummy, merge_without_dummy):
                self.assertEqual(merge_values(merge, a, b), expected, (merge.__name__, a, b))

    def test_parse_sorted(self):
        """Разбор строки: нормальный ввод и мусор"""
        self.assertEqual(parse_sorted("1 2 4"), [1, 2, 4])     # пример из условия
        self.assertEqual(parse_sorted("  -3   0  0 "), [-3, 0, 0])   # минус, повтор, лишние пробелы
        self.assertEqual(parse_sorted(""), [])                  # пустая строка - пустой список
        self.assertIsNone(parse_sorted("3 1 2"))                # не отсортирован
        self.assertIsNone(parse_sorted("1 x"))                  # буква вместо числа
        self.assertIsNone(parse_sorted("1 2.5"))                # дробь
        self.assertIsNone(parse_sorted("--1"))                  # двойной минус

    def test_read_sorted(self):
        """Корректность ввода: принимается только отсортированный список целых

        Настоящего ввода с клавиатуры в тестах нет, поэтому на время проверки
        закрываем имя input одноименной глобальной переменной модуля.
        """
        global input                                        # подменять будем глобальное имя
        cases = {                                           # строка ввода -> что должно вернуться
            "1 2 4": [1, 2, 4],                             # обычный случай
            "  5  ": [5],                                   # один элемент, пробелы по краям
            "": [],                                         # пустой список
            "4 3": None,                                    # порядок нарушен
            "abc": None,                                    # буквы вместо цифр
        }
        try:                                                # подмену надо снять в любом случае
            for text, expected in cases.items():            # проверяем вводы по очереди
                input = lambda prompt, s=text: s            # вместо чтения с клавиатуры отдаем s
                self.assertEqual(read_sorted("> "), expected, text)   # ответ совпал с ожидаемым
        finally:                                            # даже если проверка не прошла
            del input                                       # имя убрали, снова работает встроенный input

# меню

MENU = {
    "1": ("Запуск", action_run),                                    # ввод данных и ответ
    "2": ("Объяснение решения", action_explanation),                # описание алгоритма
    "3": ("Оценка сложности", action_complexity),                   # время и память
    "4": ("Визуализация работы алгоритма", action_visualization),   # таблица по шагам
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
