from datetime import datetime as dt
from mongoengine import (
    EmbeddedDocument,
    IntField,
    StringField,
    ListField,
    URLField,
    DateTimeField,
)


class MensajeIn(EmbeddedDocument):
    """
    Mensaje que el bot recibe.
    """

    _id = IntField(primary_key=True)
    canal = IntField(required=True)
    autor = IntField(required=True)
    texto = StringField(required=True)
    adjunto = ListField(URLField(), default=list)
    enviado = DateTimeField(required=True)
    editado = DateTimeField(required=True)
    registrado = DateTimeField(required=True, default=dt.utcnow)
