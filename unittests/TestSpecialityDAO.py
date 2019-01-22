import unittest

from domain.entities import Speciality, Student
from db.dao import SpecialitySqlDataMapper


class TestSpecialitySave(unittest.TestCase):
    """
    Тесты, проверяющие добавление записи в БД
    """
    @classmethod
    def setUpClass(cls):
        cls.dao = SpecialitySqlDataMapper()
        cls.added_entities = []

    @classmethod
    def tearDownClass(cls):
        for entity in cls.added_entities:
            cls.dao.delete(entity.id)

    @unittest.expectedFailure
    def test_EntityTypeIsNotSupported(self):
        self.dao.save(Student())

    def test_should_AddWithMandatoryFields(self):
        speciality = self.dao.save(Speciality(name="Право"))
        self.assertIsNotNone(speciality)
        self.assertGreater(speciality.id, 0)
        self.added_entities.append(speciality)

    def test_should_AddWithAllFields(self):
        speciality = self.dao.save(Speciality(name="Банки", code="Б-01", description="Обучение банковскому делу"))
        self.assertIsNotNone(speciality)
        self.assertGreater(speciality.id, 0)
        self.added_entities.append(speciality)

    @unittest.expectedFailure
    def test_shouldNot_AddWithoutMandatoryFields(self):
        self.dao.save(Speciality())

    # @unittest.expectedFailure
    def test_shouldNot_AddWithDuplicateID(self):
        speciality_1 = self.dao.save(Speciality(name="Специальность1"))
        self.assertIsNotNone(speciality_1)
        self.assertGreater(speciality_1.id, 0)
        self.added_entities.append(speciality_1)

        # SpecialitySqlDataMapper().save(Speciality(sp_id=speciality_1.id, name="Специальность2"))
        self.dao.save(Speciality(sp_id=speciality_1.id, name="Специальность2"))


class TestSpecialityFind(unittest.TestCase):
    """
    Тесты, проверяющие поиск записи в БД
    """
    @classmethod
    def setUpClass(cls):
        cls.dao = SpecialitySqlDataMapper()
        cls.test_entities = [
            cls.dao.save(Speciality(name="Банки", code="Б-01", description="Обучение банковскому делу")),
            cls.dao.save(Speciality(name="Право", code="П-01", description="Программа для юристов"))
        ]

    @classmethod
    def tearDownClass(cls):
        for entity in cls.test_entities:
            cls.dao.delete(entity.id)

    def setUp(self):
        self.assertEqual(len(self.test_entities), 2)

    def test_should_findEntity(self):
        last_speciality = max(self.test_entities)
        speciality = self.dao.find_by_id(last_speciality.id)
        self.assertIsNotNone(speciality)
        self.assertEqual(speciality, last_speciality)

    def test_shouldNot_findEntity(self):
        last_speciality = max(self.test_entities)
        speciality = self.dao.find_by_id(last_speciality.id + 1)
        self.assertIsNone(speciality)

    def test_should_findAllEntities(self):
        records = self.dao.find_all()
        self.assertIsNotNone(records)
        self.assertGreater(len(records), 0)


class TestSpecialityRemove(unittest.TestCase):
    """
    Тесты, проверяющие удаление записи из БД
    """
    @classmethod
    def setUpClass(cls):
        cls.dao = SpecialitySqlDataMapper()
        cls.test_entity = cls.dao.save(Speciality(name="Кибернетика", code="К-01", description="ИТ"))

    @classmethod
    def tearDownClass(cls):
        cls.dao.delete(cls.test_entity.id)

    def test_should_removeExistEntity(self):
        removed_rows = self.dao.delete(self.test_entity.id)
        self.assertEqual(removed_rows, 1)

    def test_should_removeNonExistEntity(self):
        search_id = self.test_entity.id + 1
        removed_rows = self.dao.delete(search_id)
        self.assertEqual(removed_rows, 0)

    @unittest.expectedFailure
    def test_shouldNot_removeFromNonExistTable(self):
        dao = SpecialitySqlDataMapper()
        dao._SQL_DELETE = "DELETE FROM Speciality1 where id = ?"
        dao.delete(self.test_entity.id + 1)


class TestSpecialityUpdate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dao = SpecialitySqlDataMapper()
        cls.test_record = cls.dao.save(Speciality(name="Кибернетика", code="К-01", description="ИТ"))

    @classmethod
    def tearDownClass(cls):
        cls.dao.delete(cls.test_record.id)

    @unittest.expectedFailure
    def test_EntityTypeIsNotSupported(self):
        self.dao.update(Student())

    def test_should_updateEntity(self):
        updated_rows = self.dao.update(
            Speciality(sp_id=self.test_record.id, name="Право", code="П-01", description=None)
        )
        self.assertEqual(updated_rows, 1)

        upd_record = self.dao.find_by_id(self.test_record.id)
        self.assertIsNotNone(upd_record)
        self.assertEqual(upd_record.id, self.test_record.id)
        self.assertNotEqual(upd_record.name, self.test_record.name)
        self.assertNotEqual(upd_record.code, self.test_record.code)
        self.assertNotEqual(upd_record.description, self.test_record.description)

    def test_shouldNot_updateEntity(self):
        updated_rows = self.dao.update(
            Speciality(sp_id=(self.test_record.id + 1), name="Право", code="П-01", description=None)
        )
        self.assertEqual(updated_rows, 0)

        upd_record = self.dao.find_by_id(self.test_record.id + 1)
        self.assertIsNone(upd_record)

# testLoad = unittest.TestLoader()
# # suites = testLoad.loadTestsFromModule(os.path.basename(os.path.splitext(__file__)[0]))
# suites = testLoad.loadTestsFromModule("TestSpecialityDAO")
#
# runner = unittest.TextTestRunner(verbosity=2)
# runner.run(suites)
