import os
import time
import logging
import hashlib
from functools import wraps


def load_settings(module):
    """Convert module attributes to a dictionary, ignoring private attributes."""
    settings_dict = {attr: getattr(module, attr) for attr in dir(module) if not attr.startswith('_')}
    return settings_dict


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def hash_(string):
    return hashlib.sha1(string.encode()).hexdigest()


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def timer(func):
    """
    Декоратор для измерения времени выполнения функции.
    """
    @wraps(func)  # Сохраняет метаданные исходной функции (name, docstring и т.д.)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Засекаем время перед выполнением
        result = func(*args, **kwargs)  # Выполняем функцию
        end_time = time.time()  # Засекаем время после выполнения
        execution_time = end_time - start_time  # Вычисляем время выполнения
        print(f"Функция '{func.__name__}' выполнена за {execution_time:.4f} секунд")
        return result  # Возвращаем результат исходной функции

    return wrapper


def log(name, filename=None):
    format = '%(asctime)s : %(lineno)d : %(name)s : %(levelname)s : %(message)s'
    # создаём logger
    logger = logging.getLogger(name)

    if os.environ.get('BASIC_LOG_LEVEL'):
        logging.basicConfig(
            level=int(os.environ.get('BASIC_LOG_LEVEL')),
            format=format
        )

    logger.setLevel(int(os.environ.get('LOGGING_LEVEL', 10)))
    # logger.propagate = False

    # создаём консольный handler и задаём уровень
    if filename:
        ch = logging.FileHandler(filename)
    else:
        ch = logging.StreamHandler()

    # создаём formatter
    formatter = logging.Formatter(format)
    # %(lineno)d :
    # добавляем formatter в ch
    ch.setFormatter(formatter)

    # добавляем ch к logger
    logger.addHandler(ch)

    # logger.debug('debug message')
    # logger.info('info message')
    # logger.warn('warn message')
    # logger.error('error message')
    # logger.critical('critical message')
    return logger
