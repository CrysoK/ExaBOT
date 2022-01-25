from datetime import datetime as dt
from embedded import MensajeIn
from mongoengine import (
    Document,
    IntField,
    ListField,
    BooleanField,
    EmbeddedDocumentListField,
    DateTimeField,
)


class Tickets(Document):
    """
    Datos usados en un ticket.
    """

    meta = {"collection": "tickets"}

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    usuario = IntField(required=True)
    activo = BooleanField(required=True, default=True)
    abierto = ListField(
        DateTimeField(), required=True, default=lambda: [dt.utcnow()]
    )
    cerrado = ListField(DateTimeField())
    miembros = ListField(IntField(), required=True)
    mensajes = EmbeddedDocumentListField(MensajeIn)
