from mongoengine import (
    Document,
    IntField,
)


class Usuarios(Document):
    """
    Datos de un usuario que pertenece a múltiples espacios.
    """

    meta = {"collection": "usuarios"}

    _id = IntField(primary_key=True)
