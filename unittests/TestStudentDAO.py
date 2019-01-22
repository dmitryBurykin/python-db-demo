import unittest
import copy

from domain.entities import Speciality, Student
from db.dao import SpecialitySqlDataMapper, StudentSqlDataMapper


class TestStudentSave(unittest.TestCase):
    """
    Тесты, проверяющие добавление записи в БД
    """
    @classmethod
    def setUpClass(cls):
        cls.speciality_dao = SpecialitySqlDataMapper()
        cls.student_dao = StudentSqlDataMapper()
        cls.added_students = []
        cls.test_speciality = cls.speciality_dao.save(Speciality(name="Право"))

    @classmethod
    def tearDownClass(cls):

        # Удалить тестовые записи студентов
        for student in cls.added_students:
            cls.student_dao.delete(student.id)

        # Удалить тестовые записи специальностей
        cls.speciality_dao.delete(cls.test_speciality.id)

    @unittest.expectedFailure
    def test_EntityTypeIsNotSupported(self):
        self.student_dao.save(Speciality())

    def test_should_AddWithMandatoryFields(self):
        student = Student(name="Иванов И.И.", age=18, sex="М", speciality=self.test_speciality)
        self.student_dao.save(student)
        self.added_students.append(student)

        self.assertIsNotNone(student.id)
        self.assertGreater(student.id, 0)

    @unittest.expectedFailure
    def test_shouldNot_AddWithoutName(self):
        student = Student(name=None, age="18", sex="М", speciality=self.test_speciality)
        self.student_dao.save(student)

    @unittest.expectedFailure
    def test_shouldNot_AddWithoutAge(self):
        student = Student(name="Иванов И.И.", age=None, sex="М", speciality=self.test_speciality)
        self.student_dao.save(student)

    @unittest.expectedFailure
    def test_shouldNot_AddWithoutSex(self):
        student = Student(name="Иванов И.И.", age=20, sex=None, speciality=self.test_speciality)
        self.student_dao.save(student)

    @unittest.expectedFailure
    def test_shouldNot_AddWithoutSpeciality(self):
        student = Student(name="Иванов И.И.", age=21, sex="М", speciality=None)
        self.student_dao.save(student)

    @unittest.expectedFailure
    def test_shouldNot_AddDuplicateEntity(self):
        student1 = Student(name="Петров П.П.", age=18, sex="М", speciality=self.test_speciality)
        self.student_dao.save(student1)
        self.assertGreater(student1.id, 0)
        self.added_students.append(student1)

        student2 = copy.deepcopy(student1)
        student2.name, student2.sex = "Маркова А.А.", "Ж"

        self.assertNotEqual(student2, student1)
        self.assertEqual(student2.id, student1.id)
        self.student_dao.save(student2)


class TestStudentFind(unittest.TestCase):
    """
    Тесты, проверяющие поиск записи в БД
    """
    @classmethod
    def setUpClass(cls):
        cls.speciality_dao = SpecialitySqlDataMapper()
        cls.student_dao = StudentSqlDataMapper()
        cls.test_speciality = cls.speciality_dao.save(Speciality(name="Право"))
        cls.test_students = [

            # Студент с несуществ. спец-тью
            cls.student_dao.save(Student(name="Петров П.П.", age=19, sex="М", speciality=Speciality(
                sp_id=(cls.test_speciality.id + 1),
                name="Бла-бла"
            ))),
            cls.student_dao.save(Student(name="Иванов И.И.", age=18, sex="М", speciality=cls.test_speciality)),
            cls.student_dao.save(Student(name="Маркова А.И.", age=20, sex="Ж", speciality=cls.test_speciality))
        ]

    @classmethod
    def tearDownClass(cls):

        # Удалить тестовые записи студентов
        for student in cls.test_students:
            cls.student_dao.delete(student.id)

        # Удалить тестовые записи специальностей
        cls.speciality_dao.delete(cls.test_speciality.id)

    def test_should_findAllEntities(self):
        records = self.student_dao.find_all()
        self.assertIsNotNone(records)
        self.assertGreater(len(records), 0)

    def test_shouldNot_FindEntity(self):
        last_student = max(self.test_students)
        non_exist_student = self.student_dao.find_by_id(last_student.id + 1)
        self.assertIsNone(non_exist_student)

    def test_should_FindEntity(self):
        last_student = max(self.test_students)
        student = self.student_dao.find_by_id(last_student.id)
        self.assertIsNotNone(student)
        self.assertEqual(student, last_student)

    def test_should_FindEntityWithoutSpec(self):
        first_student = min(self.test_students)
        student_wo_spec = self.student_dao.find_by_id(first_student.id)
        self.assertIsNotNone(student_wo_spec)
        # self.assertEqual(student_wo_spec, first_student)
        self.assertIsNone(student_wo_spec.speciality)

