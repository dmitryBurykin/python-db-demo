import os

# Корень проекта
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Исп. БД
SQLITE_CONNECTION_STR = os.path.join(_PROJECT_ROOT, "studentsdb.db")
