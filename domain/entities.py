from abc import ABCMeta, abstractmethod, abstractproperty


class Entity(metaclass=ABCMeta):

    @abstractproperty
    def dict(self):
        pass


class Student(Entity):
    """
    Класс домена - сущность "Студент"
    """
    def __init__(self, student_id=None, name=None, age=None, sex=None, speciality=None):
        self.id = student_id
        self.name = name
        self.age = age
        self.sex = sex
        self.speciality = speciality

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "speciality_id": self.speciality.id if self.speciality else None
        }

    def __str__(self):
        return "Student:" + str(self.dict)

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id and self.name == other.name and self.age == other.age and \
                    self.sex == other.sex and self.speciality == other.speciality
        else:
            return False


class Speciality(Entity):
    """
    Класс домена - сущность "Специальность"
    """
    def __init__(self, sp_id=None, name=None, description=None, code=None):
        self.id = sp_id
        self.name = name
        self.description = description
        self.code = code

    @property
    def dict(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "code": self.code}

    def __str__(self):
        return "Speciality:" + str(self.dict)

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id and self.name == other.name and self.description == other.description and \
                    self.code == other.code
        else:
            return False
