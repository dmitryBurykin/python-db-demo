import sqlite3

from abc import abstractmethod, ABCMeta

from properties import SQLITE_CONNECTION_STR
from domain.entities import Student, Speciality


class Databases:
    SQLITE = "sqlite"
    MYSQL = "mysql"


class ConnectionManager(metaclass=ABCMeta):
    """
    Класс, управляющий соединением с БД
    """

    @abstractmethod
    def get_connection(self):
        """
        Метод для получения соединения с БД \n
        :return: объект соединения с БД
        """
        pass

    @abstractmethod
    def close_connection(self):
        """
        Метод закрывает соединение с БД
        """
        pass

    @staticmethod
    def factory(db_type=None):
        """
        Фабричный метод, возвращающий соединение с БД указанного типа \n
        :param db_type: тип БД, к которой необходимо подключиться (MySQL, Sqlite и пр.).
        По-умолчанию = Sqlite
        :return: объект подключения к БД
        """
        if db_type is None:
            db_type = Databases.SQLITE

        if db_type == Databases.SQLITE:
            return SqliteConnectionManager()
        elif db_type == Databases.MYSQL:
            return MySqlConnectionManager()
        else:
            raise TypeError("Не реализовано подключение к БД: '{0}'".format(db_type))


class SqliteConnectionManager(ConnectionManager):
    """
    Класс подключения к БД SQLITE
    """
    def __init__(self):
        # Создать подключение к БД (sqlite)
        self.__connection = sqlite3.connect(SQLITE_CONNECTION_STR)

        # Указть преобразователи модели данных
        # sqlite3.register_adapter(Speciality, ModelAdapters.speciality_adapter)
        # sqlite3.register_adapter(Student, ModelAdapters.student_adapter)

    def get_connection(self):
        return self.__connection

    def close_connection(self):
        self.__connection.close()


class MySqlConnectionManager(ConnectionManager):
    """
    Класс подключения к БД MySQL
    """
    def close_connection(self):
        raise NotImplementedError("Метод не реализован!")

    def get_connection(self):
        raise NotImplementedError("Метод не реализован!")


class ModelAdapters:
    """
    Класс, содержит методы преобразования сущностей в объект БД
    """
    @staticmethod
    def speciality_adapter(speciality):
        if not (isinstance(speciality, Speciality)):
            raise TypeError("Указанная сущность не поддерживается адаптером: [%s].".format(type(speciality)))
        return "{0}|{1}|{2}|{3}".format(speciality.id, speciality.name, speciality.description, speciality.code)

    @staticmethod
    def student_adapter(student):
        if not (isinstance(student, Student)):
            raise TypeError("Указанная сущность не поддерживается адаптером: [%s].".format(type(student)))
        raise NotImplementedError("Метод не реализован")
