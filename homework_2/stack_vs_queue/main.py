# Домашняя работа 2. Задача 1. Stack vs queue
# Максим Царьков

import random                           # для случайных последовательностей операций в тестах
import unittest                         # стандартный модуль для тестов

TITLE = "Задача 1. Stack vs queue"   # заголовок, который печатается над меню

# решение

class Node:
    """Узел односвязного списка: значение и ссылка на следующий узел."""

    def __init__(self, value, next_node=None):
        self.value = value              # что хранит узел
        self.next = next_node           # следующий узел или None, если этот последний


class Stack:
    """Стек (LIFO) на односвязном списке.

    Вершина стека - голова списка. Кладем на голову и снимаем с головы,
    поэтому ни в одной операции не приходится идти по списку.
    """

    def __init__(self):
        self.head = None                # вершина стека, None - стек пуст
        self.size = 0                   # сколько элементов лежит в стеке

    def push(self, value):
        """Кладет value на вершину."""
        self.head = Node(value, self.head)  # новый узел ссылается на старую вершину
        self.size += 1                      # элементов стало на один больше

    def pop(self):
        """Снимает верхний элемент и возвращает его."""
        if self.head is None:                           # снимать нечего
            raise IndexError("pop из пустого стека")    # ведем себя как list.pop()
        node = self.head                # запоминаем вершину
        self.head = node.next           # вершиной становится следующий узел
        self.size -= 1                  # элементов стало на один меньше
        return node.value               # отдаем снятое значение

    def peek(self):
        """Возвращает верхний элемент, не снимая его."""
        if self.head is None:                           # смотреть не на что
            raise IndexError("peek в пустом стеке")     # та же ошибка, что у pop
        return self.head.value          # стек не меняется

    def is_empty(self):
        return self.head is None        # пустоту определяем по ссылке, а не по значению

    def __len__(self):
        return self.size                # счетчик ведем сами, узлы не пересчитываем

    def __iter__(self):
        """Обход от вершины вниз. Нужен для вывода и тестов, стек не меняет."""
        node = self.head                # начинаем с вершины
        while node is not None:         # пока не дошли до конца списка
            yield node.value            # отдаем значение
            node = node.next            # и переходим к следующему узлу


class Queue:
    """Очередь (FIFO) на односвязном списке.

    Забираем с головы (head), добавляем в хвост (tail). Ссылку на хвост храним
    отдельно, иначе для добавления пришлось бы каждый раз идти через весь список.
    """

    def __init__(self):
        self.head = None                # начало очереди, отсюда забираем
        self.tail = None                # конец очереди, сюда добавляем
        self.size = 0                   # сколько элементов стоит в очереди

    def enqueue(self, value):
        """Ставит value в конец очереди."""
        node = Node(value)              # новый узел будет последним, его next = None
        if self.tail is None:           # очередь пуста
            self.head = node            # единственный узел - это и начало
        else:                           # в очереди уже кто-то есть
            self.tail.next = node       # подцепляем узел за текущим последним
        self.tail = node                # в обоих случаях он теперь конец
        self.size += 1                  # элементов стало на один больше

    def dequeue(self):
        """Забирает первый элемент очереди и возвращает его."""
        if self.head is None:                               # забирать нечего
            raise IndexError("dequeue из пустой очереди")   # ведем себя как list.pop()
        node = self.head                # запоминаем первый узел
        self.head = node.next           # первым становится следующий
        if self.head is None:           # забрали последний элемент
            self.tail = None            # иначе tail остался бы на удаленном узле
        self.size -= 1                  # элементов стало на один меньше
        return node.value               # отдаем забранное значение

    def peek(self):
        """Возвращает первый элемент очереди, не забирая его."""
        if self.head is None:                               # смотреть не на что
            raise IndexError("peek в пустой очереди")       # та же ошибка, что у dequeue
        return self.head.value          # очередь не меняется

    def is_empty(self):
        return self.head is None        # пустоту определяем по ссылке, а не по значению

    def __len__(self):
        return self.size                # счетчик ведем сами, узлы не пересчитываем

    def __iter__(self):
        """Обход от начала к концу. Нужен для вывода и тестов, очередь не меняет."""
        node = self.head                # начинаем с первого
        while node is not None:         # пока не дошли до конца списка
            yield node.value            # отдаем значение
            node = node.next            # и переходим к следующему узлу


def chain(structure):
    """Строка вида '3 -> 2 -> 1' для вывода. Пустая структура - 'пусто'."""
    text = " -> ".join(str(v) for v in structure)   # идем по узлам от head
    return text if text else "пусто"                # у пустой структуры узлов нет

def node_text(node):
    """Значение узла для таблицы, None печатаем как есть."""
    return "None" if node is None else str(node.value)

def read_items(prompt):
    """Читает элементы через пробел. Возвращает None, если не введено ничего."""
    items = input(prompt).split()       # режем строку по пробелам
    if not items:                       # пустая строка или одни пробелы
        return None                     # признак некорректного ввода
    return items                        # элементы храним строками, как ввели

# тексты

# текст для пункта 2
EXPLANATION = """\
Обе структуры построены на односвязном списке. Узел хранит значение и ссылку
на следующий узел, у последнего узла ссылка None. Сама структура помнит только
ссылки на крайние узлы и счетчик элементов. Встроенный list не используется.
Разница между стеком и очередью только в том, с какой стороны забираем.
Стек (LIFO, последним пришел - первым ушел). Вершина стека - это голова списка
head. push создает узел, который ссылается на старую голову, и делает его
новой головой. pop запоминает голову, переносит head на следующий узел и
отдает значение. Обе операции работают только с head.
Почему вершина именно в голове, а не в конце списка. Список односвязный: от
узла можно шагнуть только вперед. Добавить в конец еще можно, если хранить
ссылку на последний узел, а вот снять последний узел нельзя, не найдя
предпоследний, а для этого надо пройти весь список. В голове же и добавление,
и удаление делаются перестановкой одной ссылки.
Очередь (FIFO, первым пришел - первым ушел). Добавляем в хвост, забираем с
головы, поэтому храним две ссылки: head и tail. enqueue подцепляет новый узел
за tail и сдвигает tail на него. dequeue забирает head и сдвигает head вперед.
Направление выбрано по той же причине, что и в стеке: из головы удалять
дешево, из хвоста дорого, значит удаляем из головы, а добавляем в хвост.
Граничные случаи, в которых легко ошибиться.
Пустая очередь. В ней head и tail оба None, и подцеплять новый узел не к чему.
Поэтому enqueue в пустую очередь ставит узел и в head, и в tail.
Очередь опустела после dequeue. head стал None, но tail все еще указывает на
только что удаленный узел. Если его не обнулить, следующий enqueue подцепит
узел к удаленному, а head так и останется None: элемент пропадет. Поэтому,
когда head становится None, обнуляем и tail.
Извлечение из пустой структуры. pop, dequeue и peek бросают IndexError, так
же как list.pop() у пустого списка. Молча возвращать None нельзя: None мог
лежать в структуре как обычное значение.
По той же причине пустоту проверяем по ссылке head is None, а не по значению.
Значения в узлах могут быть любыми, в том числе None, 0 и пустая строка.
len работает через счетчик size: он меняется в каждой операции, так что
пересчитывать узлы не нужно.
Итог stack vs queue: если положить одни и те же элементы в стек и в очередь,
стек отдаст их в обратном порядке, а очередь в том же."""

# текст для пункта 3
COMPLEXITY = """\
Обозначение: n - количество элементов, лежащих в структуре.
Время:
push, pop, peek у стека и enqueue, dequeue, peek у очереди - O(1). Каждая
операция создает не больше одного узла и переставляет одну-две ссылки у head
или tail. По списку никто не ходит, поэтому от n время не зависит.
is_empty и len - O(1): проверка одной ссылки и чтение счетчика size.
Обход (он нужен только для вывода и тестов) - O(n), каждый узел один раз.
Последовательность из m любых операций выполняется за O(m).
Для сравнения: очередь на встроенном списке через list.pop(0) работала бы за
O(n) на каждое извлечение, потому что список сдвигает все оставшиеся элементы.
Здесь сдвигать нечего, меняется только ссылка head. И в отличие от list.append,
у которого O(1) только в среднем из-за перевыделения памяти, здесь O(1) в
каждой операции: память под узел выделяется отдельно, копировать ничего не надо.
Память: O(n). На каждый элемент один узел фиксированного размера: ссылка на
значение и ссылка на следующий узел. Сверх этого стек хранит head и size,
очередь еще и tail, то есть O(1). Сами операции дополнительной памяти, кроме
нового узла, не требуют."""

# пункты меню

def action_run():
    items = read_items("Введите элементы через пробел: ")                # запрашиваем данные
    if items is None:                                                   # ввод не подошел
        print("Некорректный ввод: нужен хотя бы один элемент")          # сообщаем причину
        return                                                          # возвращаемся в меню
    stack, queue = Stack(), Queue()                                     # пустые стек и очередь
    for x in items:                                                     # кладем одно и то же
        stack.push(x)                                                   # в стек
        queue.enqueue(x)                                                # и в очередь
    print(f"Стек, вершина слева:   {chain(stack)}")                     # как лежат узлы в стеке
    print(f"Очередь, начало слева: {chain(queue)}")                     # как лежат узлы в очереди
    from_stack, from_queue = [], []                                     # порядок, в котором выходят
    while not stack.is_empty():                                         # снимаем все со стека
        from_stack.append(stack.pop())
    while not queue.is_empty():                                         # забираем все из очереди
        from_queue.append(queue.dequeue())
    print(f"Порядок выхода из стека:   {' '.join(from_stack)}")         # обратный порядок
    print(f"Порядок выхода из очереди: {' '.join(from_queue)}")         # тот же порядок

def action_explanation():
    print(EXPLANATION)                  # выводим готовый текст

def action_complexity():
    print(COMPLEXITY)                   # выводим готовый текст

def trace(script, structure):
    """Прогоняет сценарий через стек или очередь и печатает состояние после каждого шага.

    Токен '-' означает извлечь, любой другой токен - положить его.
    Возвращает извлеченные значения в том порядке, в каком они выходили.
    """
    is_queue = isinstance(structure, Queue)                     # у очереди есть еще и tail
    put = structure.enqueue if is_queue else structure.push     # операция добавления
    take = structure.dequeue if is_queue else structure.pop     # операция извлечения
    put_name = "enqueue" if is_queue else "push"                # имена для таблицы
    take_name = "dequeue" if is_queue else "pop"
    tail_title = f" {'tail':>6}" if is_queue else ""            # колонка tail только у очереди
    print(f"{'шаг':>4}  {'операция':<11} {'вернула':>7} {'head':>6}{tail_title}  "
          f"{'список':<22}  комментарий")                       # шапка таблицы

    def row(step, op, result, note):
        tail = f" {node_text(structure.tail):>6}" if is_queue else ""   # tail печатаем у очереди
        print(f"{step:>4}  {op:<11} {result:>7} {node_text(structure.head):>6}{tail}  "
              f"{chain(structure):<22}  {note}")                # состояние после шага

    row("-", "начало", "", "структура пуста")                   # состояние до сценария
    taken = []                                                  # что вышло, по порядку
    for step, token in enumerate(script, 1):                    # идем по сценарию
        if token == "-":                                        # извлечение
            try:
                value = take()                                  # вызываем настоящий pop/dequeue
            except IndexError:                                  # структура была пуста
                row(step, take_name, "ошибка", "пусто, IndexError")
                continue                                        # состояние не изменилось
            taken.append(value)                                 # запоминаем порядок выхода
            if structure.is_empty() and is_queue:               # забрали последний из очереди
                note = "очередь опустела, tail = None"
            elif structure.is_empty():                          # сняли последний со стека
                note = "стек опустел"
            elif is_queue:
                note = "head сдвинулся на следующий"
            else:
                note = "вершиной стал следующий узел"
            row(step, take_name, value, note)
        else:                                                   # добавление
            put(token)                                          # вызываем настоящий push/enqueue
            if is_queue and len(structure) == 1:                # очередь была пуста
                note = "первый узел: head и tail на нем"
            elif is_queue:
                note = "узел подцеплен за tail"
            else:
                note = "новый узел стал вершиной"
            row(step, f"{put_name} {token}", "", note)
    return taken

def action_visualization():
    s = input("Сценарий через пробел, '-' значит извлечь "
              "(Enter - взять 1 2 3 - 4 - - - 5): ").strip()    # можно задать свой пример
    script = s.split() if s else "1 2 3 - 4 - - - 5".split()    # пустой ввод - пример по умолчанию
    print("\nОдин и тот же сценарий прогоняем через стек и через очередь.")
    print("Элемент - положить его, '-' - извлечь. Список печатается от head.")
    print("\nСтек: head - это вершина.\n")
    stack = Stack()                                             # пустой стек
    from_stack = trace(script, stack)                           # таблица по шагам
    print("\nОчередь: забираем с head, добавляем за tail.\n")
    queue = Queue()                                             # пустая очередь
    from_queue = trace(script, queue)                           # таблица по шагам
    print(f"\nСтек отдал:     {' '.join(map(str, from_stack)) or 'ничего'}, "
          f"остался: {chain(stack)}")
    print(f"Очередь отдала: {' '.join(map(str, from_queue)) or 'ничего'}, "
          f"осталась: {chain(queue)}")

def action_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(Tests)   # собираем все методы test_*
    unittest.TextTestRunner(verbosity=2).run(suite)              # запускаем и печатаем отчет

class Tests(unittest.TestCase):

    def test_stack_lifo(self):
        """Стек отдает элементы в обратном порядке"""
        stack = Stack()
        for x in range(1, 6):                               # кладем 1, 2, 3, 4, 5
            stack.push(x)
        self.assertEqual([stack.pop() for _ in range(5)], [5, 4, 3, 2, 1])

    def test_queue_fifo(self):
        """Очередь отдает элементы в том же порядке"""
        queue = Queue()
        for x in range(1, 6):                               # ставим 1, 2, 3, 4, 5
            queue.enqueue(x)
        self.assertEqual([queue.dequeue() for _ in range(5)], [1, 2, 3, 4, 5])

    def test_stack_vs_queue(self):
        """На одном и том же входе порядки выхода зеркальны"""
        items = ["a", "b", "c", "d"]
        stack, queue = Stack(), Queue()
        for x in items:                                     # кладем одно и то же
            stack.push(x)
            queue.enqueue(x)
        from_stack = [stack.pop() for _ in items]
        from_queue = [queue.dequeue() for _ in items]
        self.assertEqual(from_queue, items)                 # очередь сохраняет порядок
        self.assertEqual(from_stack, items[::-1])           # стек его переворачивает

    def test_empty_raises(self):
        """Граница: извлечение и peek из пустой структуры дают IndexError"""
        with self.assertRaises(IndexError):
            Stack().pop()
        with self.assertRaises(IndexError):
            Stack().peek()
        with self.assertRaises(IndexError):
            Queue().dequeue()
        with self.assertRaises(IndexError):
            Queue().peek()

    def test_empty_state(self):
        """Граница: только что созданные структуры пусты"""
        stack, queue = Stack(), Queue()
        self.assertTrue(stack.is_empty())
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(stack), 0)
        self.assertEqual(len(queue), 0)
        self.assertEqual(list(stack), [])                   # обход не дает ни одного значения
        self.assertEqual(list(queue), [])
        self.assertIsNone(queue.tail)                       # у пустой очереди нет и хвоста

    def test_single_element(self):
        """Граница: один элемент - одновременно head и tail"""
        queue = Queue()
        queue.enqueue(7)
        self.assertIs(queue.head, queue.tail)               # это один и тот же узел
        self.assertEqual(queue.dequeue(), 7)
        self.assertIsNone(queue.head)                       # после извлечения обе ссылки пусты
        self.assertIsNone(queue.tail)
        stack = Stack()
        stack.push(7)
        self.assertEqual(stack.pop(), 7)
        self.assertTrue(stack.is_empty())

    def test_reuse_after_empty(self):
        """Структура опустела и снова наполняется: на этом ломается очередь без обнуления tail"""
        queue = Queue()
        queue.enqueue(1)
        queue.enqueue(2)
        queue.dequeue()
        queue.dequeue()                                     # очередь опустела
        queue.enqueue(3)
        queue.enqueue(4)                                    # и наполнилась заново
        self.assertEqual(list(queue), [3, 4])
        self.assertEqual(queue.dequeue(), 3)
        self.assertEqual(queue.dequeue(), 4)
        self.assertTrue(queue.is_empty())
        stack = Stack()
        stack.push(1)
        stack.pop()                                         # стек опустел
        stack.push(2)
        stack.push(3)                                       # и наполнился заново
        self.assertEqual(list(stack), [3, 2])

    def test_error_keeps_state(self):
        """После ошибки на пустой структуре она остается рабочей"""
        stack, queue = Stack(), Queue()
        with self.assertRaises(IndexError):
            stack.pop()
        with self.assertRaises(IndexError):
            queue.dequeue()
        stack.push("x")
        queue.enqueue("x")
        self.assertEqual(len(stack), 1)                     # счетчик не ушел в минус
        self.assertEqual(len(queue), 1)
        self.assertEqual(stack.pop(), "x")
        self.assertEqual(queue.dequeue(), "x")

    def test_peek_does_not_remove(self):
        """peek показывает крайний элемент и ничего не забирает"""
        stack, queue = Stack(), Queue()
        for x in (1, 2, 3):
            stack.push(x)
            queue.enqueue(x)
        self.assertEqual(stack.peek(), 3)                   # вершина стека - последний
        self.assertEqual(stack.peek(), 3)                   # повторный peek то же самое
        self.assertEqual(queue.peek(), 1)                   # начало очереди - первый
        self.assertEqual(queue.peek(), 1)
        self.assertEqual(len(stack), 3)                     # ничего не пропало
        self.assertEqual(len(queue), 3)

    def test_len_and_is_empty(self):
        """Счетчик и признак пустоты меняются вместе с операциями"""
        stack, queue = Stack(), Queue()
        for i in range(1, 4):                               # растем до трех
            stack.push(i)
            queue.enqueue(i)
            self.assertEqual(len(stack), i)
            self.assertEqual(len(queue), i)
            self.assertFalse(stack.is_empty())
            self.assertFalse(queue.is_empty())
        for i in range(2, -1, -1):                          # убываем до нуля
            stack.pop()
            queue.dequeue()
            self.assertEqual(len(stack), i)
            self.assertEqual(len(queue), i)
        self.assertTrue(stack.is_empty())
        self.assertTrue(queue.is_empty())

    def test_falsy_values(self):
        """None, 0 и пустая строка - обычные значения, а не признак пустоты"""
        stack, queue = Stack(), Queue()
        for x in (None, 0, ""):
            stack.push(x)
            queue.enqueue(x)
        self.assertFalse(stack.is_empty())
        self.assertFalse(queue.is_empty())
        self.assertEqual(len(stack), 3)
        self.assertEqual([stack.pop() for _ in range(3)], ["", 0, None])
        self.assertEqual([queue.dequeue() for _ in range(3)], [None, 0, ""])
        self.assertTrue(stack.is_empty())                   # а вот теперь действительно пусто
        self.assertTrue(queue.is_empty())

    def test_iteration_does_not_change(self):
        """Обход идет от head и структуру не меняет"""
        stack, queue = Stack(), Queue()
        for x in (1, 2, 3):
            stack.push(x)
            queue.enqueue(x)
        self.assertEqual(list(stack), [3, 2, 1])            # от вершины вниз
        self.assertEqual(list(queue), [1, 2, 3])            # от начала к концу
        self.assertEqual(list(stack), [3, 2, 1])            # второй обход дает то же
        self.assertEqual(len(queue), 3)

    def test_independent_instances(self):
        """Два экземпляра не делят данные между собой"""
        a, b = Stack(), Stack()
        a.push(1)
        self.assertTrue(b.is_empty())
        q1, q2 = Queue(), Queue()
        q1.enqueue(1)
        q2.enqueue(2)
        self.assertEqual(list(q1), [1])
        self.assertEqual(list(q2), [2])

    def test_large(self):
        """100 000 элементов: без рекурсии и без обхода списка в операциях"""
        n = 100000
        stack, queue = Stack(), Queue()
        for i in range(n):
            stack.push(i)
            queue.enqueue(i)
        self.assertEqual(len(stack), n)
        self.assertEqual(len(queue), n)
        for i in range(n):                                  # проверяем весь порядок выхода
            self.assertEqual(stack.pop(), n - 1 - i)
            self.assertEqual(queue.dequeue(), i)
        self.assertTrue(stack.is_empty())
        self.assertTrue(queue.is_empty())

    def test_against_list_model(self):
        """Сверка со встроенным списком на случайных последовательностях операций"""
        rnd = random.Random(42)                             # фиксируем seed, тест воспроизводим
        for _ in range(300):                                # 300 случайных сценариев
            stack, queue = Stack(), Queue()
            model_stack, model_queue = [], []               # эталон на обычных списках
            for _ in range(rnd.randint(0, 60)):             # до 60 операций в сценарии
                if rnd.random() < 0.55:                     # добавление чуть чаще извлечения
                    x = rnd.randint(-100, 100)
                    stack.push(x)
                    queue.enqueue(x)
                    model_stack.append(x)
                    model_queue.append(x)
                elif model_stack:                           # есть что извлекать
                    self.assertEqual(stack.pop(), model_stack.pop())
                    self.assertEqual(queue.dequeue(), model_queue.pop(0))
                else:                                       # извлечение из пустой
                    with self.assertRaises(IndexError):
                        stack.pop()
                    with self.assertRaises(IndexError):
                        queue.dequeue()
                self.assertEqual(list(stack), model_stack[::-1])    # содержимое совпало
                self.assertEqual(list(queue), model_queue)
                self.assertEqual(len(stack), len(model_stack))      # счетчик совпал
                self.assertEqual(len(queue), len(model_queue))

    def test_read_items(self):
        """Корректность ввода: нужен хотя бы один элемент

        Настоящего ввода с клавиатуры в тестах нет, поэтому на время проверки
        закрываем имя input одноименной глобальной переменной модуля.
        """
        global input                                        # подменять будем глобальное имя
        cases = {                                           # строка ввода -> что должно вернуться
            "1 2 3": ["1", "2", "3"],                       # обычный случай
            "a": ["a"],                                     # один элемент
            "  x   y  ": ["x", "y"],                        # лишние пробелы срезаются
            "": None,                                       # пустая строка
            "     ": None,                                  # одни пробелы
        }
        try:                                                # подмену надо снять в любом случае
            for text, expected in cases.items():            # проверяем вводы по очереди
                input = lambda prompt, s=text: s            # вместо чтения с клавиатуры отдаем s
                self.assertEqual(read_items("> "), expected, text)   # ответ совпал с ожидаемым
        finally:                                            # даже если проверка не прошла
            del input                                       # имя убрали, снова работает встроенный input

# меню

MENU = {
    "1": ("Запуск", action_run),                                    # ввод данных и ответ
    "2": ("Объяснение решения", action_explanation),                # описание алгоритма
    "3": ("Оценка сложности", action_complexity),                   # время и память
    "4": ("Визуализация работы алгоритма", action_visualization),   # таблицы по шагам
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
