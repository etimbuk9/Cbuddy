from django.db import models

# Create your models here.

class Student:
    def __init__(self, name, regno, student_set) -> None:
        self.name = name
        self.regno = regno
        self.student_set = student_set