from datetime import datetime as dt
from embedded import MensajeIn
from mongoengine import (
    Document,
    IntField,
    StringField,
    EmbeddedDocumentListField,
    DateTimeField,
)


class Bans(Document):
    """
    Datos relevantes de un ban.
    """

    meta = {"collection": "bans"}

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    # Infractor
    usuario = IntField(required=True)
    # Responsable
    autor = IntField(required=True)
    motivo = StringField(default="Motivo no indicado")
    evidencia = EmbeddedDocumentListField(MensajeIn)
    inicio = DateTimeField(required=True, default=dt.utcnow)
    fin = DateTimeField(required=True)
