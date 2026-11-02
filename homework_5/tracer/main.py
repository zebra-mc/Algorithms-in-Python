# Домашняя работа 5. Задача 1. Tracer
# Максим Царьков

import functools

INDENT = "  "

# Сколько вызовов декорированных функций начато и еще не завершено. Счетчик общий
# для всех функций с @tracer: тогда и взаимная рекурсия (одна функция вызывает
# другую) рисуется с правильной вложенностью.
_depth = 0


def format_call(name, args, kwargs):
    """Запись вызова вида 'f(1, 'a', key=2)': аргументы через repr, как в коде."""
    parts = [repr(a) for a in args]
    parts += [f"{key}={value!r}" for key, value in kwargs.items()]
    return f"{name}({', '.join(parts)})"


def tracer(func):
    """Декоратор, печатающий стек вызовов рекурсивной функции.

    Вход в вызов:     '<отступ>→ f(args)'
    Возврат:          '<отступ>← f(args) = результат'
    Выход с ошибкой:  '<отступ>← f(args) ! ТипИсключения: сообщение'

    Отступ – INDENT, повторенный столько раз, сколько декорированных вызовов
    уже открыто выше текущего. Результат и исключения функции не меняются.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _depth
        # Строку вызова запоминаем на входе: если функция изменит изменяемый
        # аргумент (список), строка возврата все равно совпадет со строкой входа
        call = format_call(func.__name__, args, kwargs)
        level = _depth
        print(f"{INDENT * level}→ {call}")
        _depth += 1
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            print(f"{INDENT * level}← {call} ! {type(exc).__name__}: {exc}")
            raise
        finally:
            # Выполняется при любом выходе из func, поэтому глубина
            # восстанавливается и после исключения
            _depth -= 1
        print(f"{INDENT * level}← {call} = {result!r}")
        return result

    return wrapper


@tracer
def factorial(n):
    """n! – линейная рекурсия: каждый вызов порождает не более одного дочернего."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


@tracer
def fibonacci(n):
    """n-е число Фибоначчи (F(0) = 0, F(1) = 1) – ветвящаяся рекурсия."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    print("Линейная рекурсия: factorial(4)")
    factorial(4)
    print()
    print("Ветвящаяся рекурсия: fibonacci(4)")
    fibonacci(4)


if __name__ == "__main__":
    main()
