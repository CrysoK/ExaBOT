from mongoengine import (
    Document,
    IntField,
)


class Mensajes(Document):
    """
    Datos de mensajes que el bot debe observar constantemente para cumplir con
    ciertas funciones. Los id de los mensajes son únicos para todo Discord por
    lo que no es necesario el id del espacio ni del canal al que pertenecen.
    """

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    canal = IntField(required=True)
