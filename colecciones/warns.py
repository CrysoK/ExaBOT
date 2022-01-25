from datetime import datetime as dt
from embedded import MensajeIn
from mongoengine import (
    Document,
    IntField,
    StringField,
    EmbeddedDocumentListField,
    DateTimeField,
)


class Warns(Document):
    """
    Datos relevantes de una advertencia (warn).
    """

    meta = {"collection": "warns"}

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    # Infractor
    usuario = IntField(required=True)
    # Responsable
    autor = IntField(required=True)
    motivo = StringField(default="Motivo no indicado")
    evidencia = EmbeddedDocumentListField(MensajeIn)
    fecha = DateTimeField(required=True, default=dt.utcnow)
