# Домашняя работа 3. Задача 3. Создание хеш-таблицы
# Максим Царьков

EMPTY = object()            # ячейка ни разу не занималась (лежит в hashes, не в keys)
DELETED = object()          # ячейка освобождена удалением (лежит в hashes, не в keys)
MIN_CAPACITY = 8
HASH_MOD = 2 ** 61 - 1


def string_hash(s):
    """Полиномиальный хеш строки: s[0] * 31^(n-1) + ... + s[n-1] по модулю 2^61 - 1.

    Встроенный hash() у строк меняется от запуска к запуску Python,
    а этот дает одни и те же номера ячеек, поэтому пример из README
    воспроизводится один в один. Принимает только str: объект другого типа
    может быть равен строке, а хеш у него был бы другой (см. README).
    """
    # подклассы str тоже отвергаем: они могут переопределить ==
    if type(s) is not str:
        raise TypeError(f"string_hash принимает только str, а не {type(s).__name__}")
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) % HASH_MOD
    return h


def capacity_for(n):
    """Наименьшая степень двойки (не меньше 8), при которой n элементов занимают не больше половины."""
    capacity = MIN_CAPACITY
    while capacity < 2 * n:
        capacity *= 2
    return capacity


class HashTable:
    """Хеш-таблица с открытой адресацией и линейным пробированием.

    Данные лежат в трех списках длины capacity: hashes, keys, values.
    Состояние ячейки i хранится в hashes[i]: EMPTY - свободна, DELETED - удалена,
    иначе там хеш живого ключа. У живой ячейки в hashes всегда int, поэтому метки
    не совпадают с данными, и сами EMPTY и DELETED тоже могут быть ключами.
    Инвариант: (size + deleted) * 3 <= capacity * 2, поэтому хотя бы одна
    ячейка всегда свободна и поиск всегда останавливается.

    hash_func - хеш-функция ключей. Она обязана быть согласована с ==:
    из a == b должно следовать hash_func(a) == hash_func(b). По умолчанию это
    встроенный hash(), и таблица ведет себя как dict: 1, 1.0 и True - один ключ.
    HashTable(string_hash) - таблица только для строк с воспроизводимыми ячейками.
    """

    def __init__(self, hash_func=hash):
        self.hash_func = hash_func
        self._allocate(MIN_CAPACITY)

    def _allocate(self, capacity):
        """Заводит пустые списки на capacity ячеек и обнуляет счетчики."""
        self.capacity = capacity
        self.hashes = [EMPTY] * capacity
        self.keys = [None] * capacity
        self.values = [None] * capacity
        self.size = 0
        self.deleted = 0

    def _find_slot(self, key, h):
        """Ищет ключ, начиная с ячейки h % capacity и шагая вправо по кругу.

        Возвращает (индекс, найден ли ключ). Если ключа нет, индекс - место для
        вставки: первая удаленная ячейка на пути, а если ее не было - свободная
        ячейка, на которой поиск остановился.
        """
        i = h % self.capacity           # в Python % дает 0..capacity-1 и для отрицательных h
        first_deleted = None
        for _ in range(self.capacity):
            hs = self.hashes[i]
            if hs is EMPTY:
                # при вставке ключ лег бы не дальше этой ячейки, значит дальше его нет
                return (i if first_deleted is None else first_deleted), False
            if hs is DELETED:
                # останавливаться нельзя: за удаленной ячейкой цепочка продолжается
                if first_deleted is None:
                    first_deleted = i
            elif hs == h and (self.keys[i] is key or self.keys[i] == key):
                # хеши сравниваем раньше дорогого ==; is - чтобы находился NaN
                return i, True
            i = (i + 1) % self.capacity
        return first_deleted, False     # недостижимо при соблюдении инварианта

    def put(self, key, value):
        """Вставка пары. Если ключ уже есть, заменяет значение."""
        h = self.hash_func(key)
        i, found = self._find_slot(key, h)
        if found:
            self.values[i] = value
            return
        # вставка в удаленную ячейку заполнение не увеличивает, в свободную - увеличивает
        if self.hashes[i] is EMPTY and (self.size + self.deleted + 1) * 3 > self.capacity * 2:
            self._resize(capacity_for(self.size + 1))
            i, _ = self._find_slot(key, h)
        if self.hashes[i] is DELETED:
            self.deleted -= 1
        self.hashes[i] = h
        self.keys[i] = key
        self.values[i] = value
        self.size += 1

    def get(self, key, default=None):
        """Поиск по ключу. Если ключа нет, возвращает default."""
        i, found = self._find_slot(key, self.hash_func(key))
        return self.values[i] if found else default

    def remove(self, key):
        """Удаление по ключу. Возвращает значение; если ключа нет - KeyError."""
        i, found = self._find_slot(key, self.hash_func(key))
        if not found:
            raise KeyError(key)
        value = self.values[i]
        # EMPTY здесь оборвал бы поиск ключей, которые при вставке прошли через эту ячейку
        self.hashes[i] = DELETED
        self.keys[i] = None
        self.values[i] = None
        self.size -= 1
        self.deleted += 1
        if self.capacity > MIN_CAPACITY and self.size * 8 < self.capacity:
            self._resize(capacity_for(self.size))
        return value

    def _resize(self, capacity):
        """Перестраивает таблицу на capacity ячеек. Метки DELETED при этом исчезают."""
        old = zip(self.hashes, self.keys, self.values)
        self._allocate(capacity)
        for h, k, v in old:
            if h is EMPTY or h is DELETED:
                continue
            # хеш сохранен, пересчитывать не нужно; в новой таблице нет ни удаленных
            # ячеек, ни одинаковых ключей, поэтому хватает первой свободной
            i = h % capacity
            while self.hashes[i] is not EMPTY:
                i = (i + 1) % capacity
            self.hashes[i] = h
            self.keys[i] = k
            self.values[i] = v
            self.size += 1

    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        i, found = self._find_slot(key, self.hash_func(key))
        if not found:
            raise KeyError(key)
        return self.values[i]

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, key):
        return self._find_slot(key, self.hash_func(key))[1]

    def __len__(self):
        return self.size

    def items(self):
        """Пары (ключ, значение) в порядке ячеек."""
        for i in range(self.capacity):
            h = self.hashes[i]
            if h is not EMPTY and h is not DELETED:
                yield self.keys[i], self.values[i]

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def __repr__(self):
        return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in self.items()) + "}"


def slots_text(table):
    """Ячейки таблицы строкой: '.' - пусто, '-' - удалено, иначе ключ. Пример: '0:. 1:a 2:-'."""
    cells = []
    for i, (h, k) in enumerate(zip(table.hashes, table.keys)):
        if h is EMPTY:
            cells.append(f"{i}:.")
        elif h is DELETED:
            cells.append(f"{i}:-")
        else:
            cells.append(f"{i}:{k}")
    return " ".join(cells)


def parse_script(s):
    """Разбирает строку команд. None, если ввод некорректный.

    ключ=значение - вставка, ?ключ - поиск, -ключ - удаление.
    Первый символ проверяется раньше '=', поэтому '-a=1' - это удаление ключа 'a=1'.
    Возвращает список троек (операция, ключ, значение).
    """
    tokens = s.split()
    if not tokens:
        return None
    commands = []
    for token in tokens:
        if token[0] == "?":
            op, key, value = "get", token[1:], None
        elif token[0] == "-":
            op, key, value = "del", token[1:], None
        elif "=" in token:
            key, value = token.split("=", 1)
            op = "put"
        else:
            return None
        if key == "":
            return None
        commands.append((op, key, value))
    return commands


def read_script(prompt):
    """Читает строку команд с клавиатуры. None, если ввод некорректный."""
    return parse_script(input(prompt))


def execute(table, commands):
    """Выполняет команды над таблицей и возвращает строки с результатом каждой."""
    lines = []
    for op, key, value in commands:
        if op == "put":
            existed = key in table
            table.put(key, value)
            lines.append(f"{key}={value}: {'значение заменено' if existed else 'вставлен'}")
        elif op == "get":
            if key in table:
                lines.append(f"?{key}: {table[key]}")
            else:
                lines.append(f"?{key}: нет такого ключа")
        else:
            try:
                lines.append(f"-{key}: удален, значение было {table.remove(key)}")
            except KeyError:
                lines.append(f"-{key}: нет такого ключа")
    return lines


def main():
    commands = read_script("Введите команды через пробел (ключ=значение - вставка, "
                           "?ключ - поиск, -ключ - удаление): ")
    if commands is None:
        print("Некорректный ввод: нужны команды вида a=1, ?a, -a")
        return
    table = HashTable(string_hash)       # ключи из консоли - строки
    for line in execute(table, commands):
        print(line)
    print(f"Таблица: {table}")
    print(f"Элементов: {len(table)}, ячеек: {table.capacity}")
    print(f"Ячейки: {slots_text(table)}")


if __name__ == "__main__":
    main()
