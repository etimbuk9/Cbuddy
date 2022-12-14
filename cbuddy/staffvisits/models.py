from django.db import models

# Create your models here.

class Staff:
    def __init__(self, name, regno) -> None:
        self.name = name
        self.staff_id = regno