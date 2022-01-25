from mongoengine import (
    Document,
    EmbeddedDocument,
    IntField,
    StringField,
    ListField,
    URLField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
)


class MensajeOut(EmbeddedDocument):
    """
    Mensaje que el bot envía.
    """

    texto = StringField(required=True, default="Mensaje por defecto")
    adjunto = ListField(URLField(), default=list)
    canal = IntField()


class Respuestas(EmbeddedDocument):
    """Conjunto de mensajes que el bot envía como respuesta a un comando o
    evento."""

    humanos = EmbeddedDocumentListField(MensajeOut)
    bots = EmbeddedDocumentListField(MensajeOut)
    canal = IntField(required=True, default=0)


class Espacios(Document):
    """
    Datos relacionados a un espacio en particular.
    """

    meta = {"collection": "espacios"}

    _id = IntField(primary_key=True)
    prefix = ListField(StringField(), default=lambda: ["?"])
    # `casos` indica la cantidad de warns, kicks, bans, etc. Se incrementa cada
    # vez que se registra uno para asignarle un id único.
    casos = IntField(required=True, default=0)
    entrada = EmbeddedDocumentField(Respuestas)
    salida = EmbeddedDocumentField(Respuestas)
    ban = EmbeddedDocumentField(Respuestas)
    # Cómo implementar los canales con restricciones o los canales con
    # reacciones automáticas?
