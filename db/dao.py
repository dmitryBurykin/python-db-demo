from abc import ABCMeta, abstractmethod, abstractproperty

from utils.db import ConnectionManager, Databases
from utils.exceptions import DAOException
from domain.entities import Speciality, Student

from sqlite3 import DatabaseError


class IDataMapper(metaclass=ABCMeta):
    """
    Интерфейс, содержащий определения методов получения данных из какого-либо источника (БД / XML и пр.)
    """

    @abstractmethod
    def save(self, entity):
        """
        Метод сохраняет сущность в источнике данных \n
        :param entity: сохраняемый объект
        :return: сохраненный в источнике объект с указанным ID
        """
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        """
        Метод возвращает из источника данных запись с указанным ID \n
        :param entity_id: ИД сущности, кот. необходимо найти
        :return: искомая сущность
        """
        pass

    @abstractmethod
    def find_all(self):
        """
        Метод возвращает все записи требуемого типа из источника данных \n
        :return: []
        """
        pass

    @abstractmethod
    def delete(self, entity_id):
        """
        Метод удаляет из источника данных запись с указанным ID \n
        :param entity_id: ИД сущности
        :return: кол-во удаленных записей
        """
        pass

    @abstractmethod
    def update(self, entity):
        """
        Метод обновляет сущность в источнике данных в соответствии с указанными параметрами
        :param entity: сущность (новые параметры записи)
        :return:
        """
        pass


class AbstractSqlDataMapper(metaclass=ABCMeta):
    """
    Класс-примесь, реализующий CRUD-операции по добавлению сущности в указанную БД
    Базовый класс преобразователь данных БД
    """
    @abstractproperty
    def database(self):
        """
        БД, на которой будут выполняться запросы \n
        :return: mysql | sqlite
        """
        pass

    def _save(self, sql, params):
        connect_manager = ConnectionManager.factory(self.database)
        cursor = connect_manager.get_connection().cursor()
        row_id = 0

        try:
            cursor.execute(sql, params)
        except DatabaseError as err:
            connect_manager.get_connection().rollback()
            raise DAOException("Не удалось добавить запись в БД: '{0}'".format(str(err))) from err
        else:
            connect_manager.get_connection().commit()
            row_id = cursor.lastrowid
            print("В БД добавлена запись! [ID={0}]".format(row_id))
        finally:
            cursor.close()
            connect_manager.close_connection()
        return row_id

    def _update(self, sql, params):
        connect_manager = ConnectionManager.factory(self.database)
        cursor = connect_manager.get_connection().cursor()
        affected_rows = 0

        try:
            cursor.execute(sql, params)
        except DatabaseError as err:
            connect_manager.get_connection().rollback()
            raise DAOException("Не удалось обновить объект в БД: '{0}'".format(str(err))) from err
        else:
            connect_manager.get_connection().commit()
            affected_rows = cursor.rowcount
            print("В БД обновлено записей: {0}".format(affected_rows))
        finally:
            cursor.close()
            connect_manager.close_connection()
        return affected_rows

    def _delete(self, sql, params):
        connect_manager = ConnectionManager.factory(self.database)
        cursor = connect_manager.get_connection().cursor()
        affected_rows = 0

        try:
            cursor.execute(sql, params)
        except DatabaseError as err:
            connect_manager.get_connection().rollback()
            raise DAOException("Не удалось удалить объект из БД: '{0}'".format(str(err))) from err
        else:
            connect_manager.get_connection().commit()
            affected_rows = cursor.rowcount
            print("Из БД удалено записей: {0}".format(affected_rows))
        finally:
            cursor.close()
            connect_manager.close_connection()
        return affected_rows

    def _find_by_id(self, sql, params):
        connect_manager = ConnectionManager.factory(self.database)
        cursor = connect_manager.get_connection().cursor()

        try:
            cursor.execute(sql, params)
        except DatabaseError as err:
            raise DAOException("Не удалось найти объект в БД. Причина: '{1}'".format(str(err))) \
                from err
        else:
            row = cursor.fetchone()  # Прочитать 1 строку результата запроса -> tuple()
        finally:
            cursor.close()
            connect_manager.close_connection()

        return row

    def _find_all(self, sql):
        connect_manager = ConnectionManager.factory(self.database)
        cursor = connect_manager.get_connection().cursor()

        try:
            cursor.execute(sql)
        except DatabaseError as err:
            raise DAOException("Не удалось получить все записи из БД. Причина: '{0}'".format(str(err))) \
                from err
        else:
            rows = cursor.fetchall()  # Прочитать все записи из результата запроса -> []
            print("Из БД получено записей: {0}".format(len(rows)))
        finally:
            cursor.close()
            connect_manager.close_connection()

        return rows


class StudentSqlDataMapper(IDataMapper, AbstractSqlDataMapper):

    def __init__(self):
        self.speciality_dao = SpecialitySqlDataMapper()
        self._SQL_UPDATE = """\
        update Student \
        set name = :name, \
          age = :age, \
          sex = :sex, \
          speciality_id = :speciality_id \
        where id = :id \
        """
        self._SQL_INSERT = """\
                            insert INTO Student(ID,NAME,AGE,sex,SPECIALITY_ID) \
                            values(:id,:name,:age,:sex,:speciality_id)
                           """
        self._SQL_FIND_ONE = "SELECT * from Student where id = ?"
        self._SQL_FIND_ALL = "SELECT * from Student"
        self._SQL_DELETE = "DELETE from Student where id = ?"

    @property
    def database(self):
        return Databases.SQLITE

    def update(self, entity):
        # super().update(entity)
        if not (isinstance(entity, Student)):
            raise TypeError("Неверный тип сущности для работы с БД: [{0}].".format(type(entity)))

        return super()._update(self._SQL_UPDATE, entity.dict)

    def delete(self, entity_id):
        return super()._delete(self._SQL_DELETE, (entity_id,))

    def find_by_id(self, entity_id):
        # super().find_by_id(entity_id)
        entity = None
        row = super()._find_by_id(self._SQL_FIND_ONE, (entity_id,))

        # Если в БД есть запись по указанному ID
        if row:
            # Получить специальность студента
            speciality_id = row[4]
            speciality = self.speciality_dao.find_by_id(speciality_id)

            entity = Student(student_id=row[0],
                             name=row[1],
                             age=row[2],
                             sex=row[3],
                             speciality=speciality)
        return entity

    def find_all(self):
        entities = []
        records = super()._find_all(self._SQL_FIND_ALL)

        # Обработать результаты поиска записей в БД
        if records:
            for record in records:

                # Получить специальность студента
                speciality_id = record[4]
                speciality = self.speciality_dao.find_by_id(speciality_id)

                # Добавить сущность студента в результ. список записей
                student = Student(student_id=record[0],
                                  name=record[1],
                                  age=record[2],
                                  sex=record[3],
                                  speciality=speciality)
                entities.append(student)

        return entities

    def save(self, entity):
        if not (isinstance(entity, Student)):
            raise TypeError("Неверный тип сущности для работы с БД: [{0}].".format(type(entity)))

        row_id = super()._save(self._SQL_INSERT, entity.dict)
        entity.id = row_id
        return entity


class SpecialitySqlDataMapper(IDataMapper, AbstractSqlDataMapper):
    """
    Класс для получения данных из таблицы БД Speciality
    """
    def __init__(self):
        self._SQL_UPDATE = """\
            UPDATE Speciality \
            SET name = :name, description = :description, code = :code \
            WHERE id = :id \
          """
        self._SQL_INSERT = """INSERT INTO SPECIALITY(ID, NAME, DESCRIPTION, CODE) \
                               VALUES (:id, :name, :description, :code)"""
        self._SQL_FIND_ONE = "SELECT * from Speciality where id = ?"
        self._SQL_FIND_ALL = "SELECT * from Speciality"
        self._SQL_DELETE = "DELETE FROM Speciality where id = ?"

    @property
    def database(self):
        return Databases.SQLITE

    # Обновление записи
    def update(self, entity):
        if not (isinstance(entity, Speciality)):
            raise TypeError("Неверный тип сущности для работы с БД: [{0}].".format(type(entity)))

        return super()._update(self._SQL_UPDATE, entity.dict)

    # Удаление записи
    def delete(self, entity_id):
        return super()._delete(self._SQL_DELETE, (entity_id,))

    # Поиск по ID
    def find_by_id(self, entity_id):

        entity = None
        row = super()._find_by_id(self._SQL_FIND_ONE, (entity_id,))

        if row is None:
            print("В БД не найден объект с ID='{0}'".format(entity_id))
        else:
            entity = Speciality(sp_id=row[0], name=row[1], description=row[2], code=row[3])
            print("В БД найден объект с ID='{0}': {1}".format(entity_id, entity))

        return entity

    # Поиск всех записей
    def find_all(self):

        entities = []
        records = super()._find_all(self._SQL_FIND_ALL)

        # Обработать результаты поиска записей в БД
        if records:
            for record in records:
                entities.append(Speciality(sp_id=record[0], name=record[1], description=record[2], code=record[3]))

        return entities

    # Сохранение записи
    def save(self, entity):
        if not (isinstance(entity, Speciality)):
            raise TypeError("Неверный тип сущности для работы с БД: [{0}].".format(type(entity)))

        row_id = super()._save(self._SQL_INSERT, entity.dict)
        entity.id = row_id
        print("В БД добавлен объект: {0}".format(entity))
        return entity
