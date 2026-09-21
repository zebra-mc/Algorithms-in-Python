# Домашняя работа 2. Задача 2. Merge lists
# Максим Царьков

import random  # нужен только для большого теста
import unittest  # модуль для тестов


# решение

class ListNode:
    """Узел односвязного списка"""

    def __init__(self, val=0, next=None):
        self.val = val  # значение узла
        self.next = next  # ссылка на следующий узел


def build_list(values):
    """Строит односвязный список из обычного списка, возвращает голову"""
    head = None  # пока список пустой
    for value in reversed(values):  # идем с конца, чтобы добавлять узлы в начало
        head = ListNode(value, head)  # новый узел становится головой
    return head


def to_array(head):
    """Переводит односвязный список в обычный список python"""
    result = []  # сюда складываем значения
    current = head  # начинаем с головы
    while current is not None:  # пока не дошли до конца
        result.append(current.val)  # запоминаем значение
        current = current.next  # переходим к следующему узлу
    return result


def merge_with_dummy(list1, list2):
    """Слияние двух отсортированных списков с фиктивным элементом"""
    dummy = ListNode()  # фиктивный узел, к нему цепляем результат
    tail = dummy  # хвост собранного списка
    while list1 is not None and list2 is not None:  # пока оба списка не кончились
        if list1.val <= list2.val:  # при равенстве берем из первого списка
            tail.next = list1  # цепляем узел из первого списка
            list1 = list1.next  # сдвигаемся в первом списке
        else:
            tail.next = list2  # цепляем узел из второго списка
            list2 = list2.next  # сдвигаемся во втором списке
        tail = tail.next  # хвост теперь на добавленном узле
    tail.next = list1 if list1 is not None else list2  # остаток цепляем целиком
    return dummy.next  # настоящая голова идет сразу после фиктивного узла


def merge_without_dummy(list1, list2):
    """Слияние двух отсортированных списков без фиктивного элемента"""
    if list1 is None:  # первый список пустой - ответ второй список
        return list2
    if list2 is None:  # второй список пустой - ответ первый список
        return list1
    if list1.val <= list2.val:  # голова - меньший из первых узлов
        head = list1  # голова из первого списка
        list1 = list1.next  # сдвигаемся в первом списке
    else:
        head = list2  # голова из второго списка
        list2 = list2.next  # сдвигаемся во втором списке
    tail = head  # хвост пока совпадает с головой
    while list1 is not None and list2 is not None:  # дальше так же, как с фиктивным
        if list1.val <= list2.val:  # при равенстве берем из первого списка
            tail.next = list1  # цепляем узел из первого списка
            list1 = list1.next  # сдвигаемся в первом списке
        else:
            tail.next = list2  # цепляем узел из второго списка
            list2 = list2.next  # сдвигаемся во втором списке
        tail = tail.next  # хвост теперь на добавленном узле
    tail.next = list1 if list1 is not None else list2  # остаток цепляем целиком
    return head  # голову запомнили в самом начале


def read_list(name, default=None):
    """Считывает отсортированный список целых чисел с клавиатуры"""
    if default is None:  # подсказка зависит от того, есть ли пример по умолчанию
        prompt = f"Введите {name} через пробел (пустая строка - пустой список): "
    else:
        prompt = f"Введите {name} через пробел (Enter - {default}): "
    while True:  # спрашиваем, пока не введут корректно
        line = input(prompt).strip()  # читаем строку
        if line == "" and default is not None:  # Enter - берем пример по умолчанию
            return list(default)
        try:
            values = [int(x) for x in line.split()]  # переводим в числа
        except ValueError:  # попалось что-то кроме целых чисел
            print("Ошибка: нужно вводить целые числа")
            continue
        if any(values[i] > values[i + 1] for i in range(len(values) - 1)):  # проверка сортировки
            print("Ошибка: список должен быть отсортирован по неубыванию")
            continue
        return values  # все хорошо


# тексты

EXPLANATION = """
Идея решения:
Оба списка уже отсортированы, поэтому самый маленький элемент ответа - это
меньший из двух первых узлов. Держим по указателю на текущий узел в каждом
списке, сравниваем их значения и меньший узел цепляем в конец результата,
после чего сдвигаем указатель в том списке, откуда взяли узел.
Когда один из списков кончился, все оставшиеся узлы другого уже отсортированы
и не меньше того, что мы взяли, поэтому хвост цепляется целиком одной операцией.
Новые узлы не создаются - меняются только ссылки next у исходных узлов.
При равных значениях берем узел из list1 (сравнение <=), слияние устойчивое.

Способ 1 - с фиктивным элементом (merge_with_dummy):
Создаем пустой узел dummy и ставим на него указатель tail. Первый узел ответа
цепляется к dummy.next так же, как и все остальные, поэтому не нужно отдельно
разбирать случай пустых списков и выбор головы. В конце возвращаем dummy.next.

Способ 2 - без фиктивного элемента (merge_without_dummy):
Сначала отдельно обрабатываем пустые списки, затем выбираем голову ответа -
меньший из двух первых узлов, и ставим на нее tail. Дальше цикл такой же,
как в первом способе, а возвращаем запомненную голову head.
"""

COMPLEXITY = """
Пусть n - длина list1, m - длина list2.

Время: O(n + m).
За одну итерацию цикла ровно один узел цепляется к результату и один из
указателей сдвигается на шаг, значит итераций не больше n + m. Остаток
цепляется одной операцией за O(1). В способе без фиктивного элемента
добавляются только проверки в начале, это O(1).

Память: O(1) дополнительной памяти в обоих способах.
Новые узлы не создаются, результат собирается из узлов исходных списков.
Используются только несколько указателей (tail, head) и в первом способе
один фиктивный узел, их количество не зависит от n и m.
"""


# пункты меню

def action_run():
    """Решение задачи на введенных данных"""
    values1 = read_list("list1")  # читаем первый список
    values2 = read_list("list2")  # читаем второй список
    # слияние портит исходные списки, поэтому для каждого способа строим свои
    result1 = merge_with_dummy(build_list(values1), build_list(values2))
    result2 = merge_without_dummy(build_list(values1), build_list(values2))
    print("С фиктивным элементом: ", to_array(result1))
    print("Без фиктивного элемента:", to_array(result2))


def action_explanation():
    """Вывод объяснения"""
    print(EXPLANATION)


def action_complexity():
    """Вывод оценки сложности"""
    print(COMPLEXITY)


def collected(dummy, tail):
    """Значения уже собранной части ответа - от dummy.next до tail"""
    result = []  # собранная часть
    current = dummy  # начинаем с фиктивного узла
    while current is not tail:  # идем до хвоста включительно
        current = current.next
        result.append(current.val)
    return result


def merge_steps(values1, values2):
    """Повторяет merge_with_dummy и запоминает состояние на каждом шаге"""
    list1 = build_list(values1)  # строим первый список
    list2 = build_list(values2)  # строим второй список
    dummy = ListNode()  # фиктивный узел как в решении
    tail = dummy  # хвост результата
    rows = []  # строки таблицы
    step = 0  # номер шага
    while list1 is not None and list2 is not None:  # тот же цикл, что в решении
        step += 1
        left = to_array(list1)  # что осталось в первом списке до шага
        right = to_array(list2)  # что осталось во втором списке до шага
        if list1.val <= list2.val:  # берем из первого
            compare = f"{list1.val} <= {list2.val}"
            taken = f"{list1.val} из list1"
            tail.next = list1
            list1 = list1.next
        else:  # берем из второго
            compare = f"{list1.val} > {list2.val}"
            taken = f"{list2.val} из list2"
            tail.next = list2
            list2 = list2.next
        tail = tail.next  # двигаем хвост
        # tail.next еще смотрит в исходный список, поэтому печатаем только до tail
        rows.append([str(step), str(left), str(right), compare, taken, str(collected(dummy, tail))])
    step += 1  # последний шаг - прицепляем остаток
    rest = list1 if list1 is not None else list2  # какой список остался
    name = "list1" if list1 is not None else "list2"  # его имя для таблицы
    tail.next = rest
    rows.append([str(step), str(to_array(list1)), str(to_array(list2)), "один пуст",
                 f"остаток {to_array(rest)} из {name}", str(to_array(dummy.next))])
    return rows, to_array(dummy.next)


def action_visualization():
    """Пошаговая визуализация слияния с фиктивным элементом"""
    values1 = read_list("list1", [1, 4, 5, 9])  # пример по умолчанию
    values2 = read_list("list2", [2, 3, 4, 10, 12])  # пример по умолчанию
    rows, result = merge_steps(values1, values2)  # считаем шаги
    header = ["Шаг", "list1", "list2", "Сравнение", "Берем", "Собрано (dummy.next ... tail)"]
    table = [header] + rows  # вся таблица вместе с заголовком
    widths = [max(len(row[i]) for row in table) for i in range(len(header))]  # ширина колонок
    for row in table:  # печатаем таблицу
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(row))))
        if row is header:  # линия под заголовком
            print("-+-".join("-" * w for w in widths))
    print("Ответ:", result)
    print("Без фиктивного элемента шаги те же, только первый узел сразу")
    print("становится head, а не цепляется к dummy.next")


def action_tests():
    """Запуск тестов"""
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)  # собираем тесты
    unittest.TextTestRunner(verbosity=2).run(suite)  # запускаем


class Tests(unittest.TestCase):
    """Тесты для обоих способов слияния"""

    def check(self, values1, values2, expected):
        """Проверяет оба способа на одних данных"""
        for merge in (merge_with_dummy, merge_without_dummy):  # по очереди оба способа
            with self.subTest(method=merge.__name__):
                result = merge(build_list(values1), build_list(values2))  # свои списки на каждый способ
                self.assertEqual(to_array(result), expected)

    def test_example(self):
        """Пример из условия"""
        self.check([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4])

    def test_both_empty(self):
        """Оба списка пустые"""
        self.check([], [], [])

    def test_first_empty(self):
        """Первый список пустой"""
        self.check([], [0], [0])

    def test_second_empty(self):
        """Второй список пустой"""
        self.check([1, 2, 3], [], [1, 2, 3])

    def test_one_element_each(self):
        """По одному элементу в каждом списке"""
        self.check([5], [3], [3, 5])
        self.check([3], [5], [3, 5])

    def test_all_equal(self):
        """Все элементы одинаковые"""
        self.check([7, 7, 7], [7, 7], [7, 7, 7, 7, 7])

    def test_negative(self):
        """Отрицательные числа и ноль"""
        self.check([-10, -3, 0, 2], [-5, -3, 1], [-10, -5, -3, -3, 0, 1, 2])

    def test_no_interleaving(self):
        """Все элементы одного списка меньше всех элементов другого"""
        self.check([1, 2, 3], [4, 5, 6], [1, 2, 3, 4, 5, 6])
        self.check([4, 5, 6], [1, 2, 3], [1, 2, 3, 4, 5, 6])

    def test_different_lengths(self):
        """Списки разной длины, длинный остаток"""
        self.check([2], [1, 3, 5, 7, 9], [1, 2, 3, 5, 7, 9])

    def test_nodes_reused(self):
        """Ответ собран из исходных узлов, новых узлов нет"""
        for merge in (merge_with_dummy, merge_without_dummy):
            with self.subTest(method=merge.__name__):
                list1 = build_list([1, 4, 6])
                list2 = build_list([2, 3, 5])
                nodes = set()  # id всех исходных узлов
                for head in (list1, list2):
                    while head is not None:
                        nodes.add(id(head))
                        head = head.next
                result = merge(list1, list2)
                merged = set()  # id узлов ответа
                while result is not None:
                    merged.add(id(result))
                    result = result.next
                self.assertEqual(nodes, merged)

    def test_stable(self):
        """При равных значениях первым идет узел из list1"""
        for merge in (merge_with_dummy, merge_without_dummy):
            with self.subTest(method=merge.__name__):
                list1 = build_list([1, 2])
                list2 = build_list([1, 2])
                first1 = list1  # узел 1 из первого списка
                second1 = list1.next  # узел 2 из первого списка
                result = merge(list1, list2)
                self.assertIs(result, first1)  # голова - из list1
                self.assertIs(result.next.next, second1)  # третий узел - двойка из list1

    def test_big_random(self):
        """Большие случайные списки, сверяем с sorted"""
        random.seed(42)  # чтобы тест был воспроизводимым
        for _ in range(20):
            values1 = sorted(random.randint(-100, 100) for _ in range(random.randint(0, 1000)))
            values2 = sorted(random.randint(-100, 100) for _ in range(random.randint(0, 1000)))
            self.check(values1, values2, sorted(values1 + values2))

    def test_read_list(self):
        """Обычный ввод списка"""
        global input
        old_input = input
        answers = iter(["1 2 4"])
        input = lambda prompt="": next(answers)  # подменяем ввод
        try:
            self.assertEqual(read_list("list1"), [1, 2, 4])
        finally:
            input = old_input  # возвращаем настоящий input

    def test_read_empty(self):
        """Пустая строка - пустой список"""
        global input
        old_input = input
        answers = iter([""])
        input = lambda prompt="": next(answers)
        try:
            self.assertEqual(read_list("list1"), [])
        finally:
            input = old_input

    def test_read_wrong_then_right(self):
        """Сначала не числа и не отсортированный список, потом правильный ввод"""
        global input
        old_input = input
        answers = iter(["1 a 3", "5 2 1", "-1 0 0 3"])
        input = lambda prompt="": next(answers)
        try:
            self.assertEqual(read_list("list1"), [-1, 0, 0, 3])
        finally:
            input = old_input

    def test_read_default(self):
        """Enter при наличии примера по умолчанию"""
        global input
        old_input = input
        answers = iter([""])
        input = lambda prompt="": next(answers)
        try:
            self.assertEqual(read_list("list1", [1, 4, 5, 9]), [1, 4, 5, 9])
        finally:
            input = old_input


# меню

MENU = """
1. Решить задачу
2. Объяснение решения
3. Оценка сложности
4. Визуализация
5. Тесты
6. Выход
"""

ACTIONS = {
    "1": action_run,
    "2": action_explanation,
    "3": action_complexity,
    "4": action_visualization,
    "5": action_tests,
}


def main():
    """Главный цикл меню"""
    while True:  # работаем, пока не выберут выход
        print(MENU)
        choice = input("Выберите пункт: ").strip()  # читаем пункт меню
        if choice == "6":  # выход
            print("Выход")
            break
        action = ACTIONS.get(choice)  # ищем нужное действие
        if action is None:  # такого пункта нет
            print("Нет такого пункта, попробуйте еще раз")
            continue
        action()  # выполняем пункт


if __name__ == "__main__":
    main()
