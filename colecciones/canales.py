from mongoengine import (
    Document,
    EmbeddedDocument,
    IntField,
    StringField,
    ListField,
    DynamicField,
    EmbeddedDocumentField,
)


class AutoReacciones(EmbeddedDocument):
    """
    Datos para la función de canales con reacciones automáticas a ciertos
    mensajes
    """

    # Solo se reaccionará a los mensajes que cumplan con el filtro. El filtro
    # es una expresión regular. Para reaccionar a todos los mensajes, no se
    # indica un filtro en el comando y queda por defecto como "[\s\S]+", que
    # acepta todos los mensajes.
    filtro = DynamicField(required=True, default=r"[\s\S]+")
    reacciones = ListField(StringField(), required=True)


class Canales(Document):
    """
    Datos de canales que el bot debe observar constantemente para cumplir con
    ciertas funciones. Los id de los canales son únicos para todo Discord por
    lo que no es necesario el id del espacio al que pertenecen.
    """

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    # Para desactivar las funciones simplemente deben ser None
    autoreacciones = EmbeddedDocumentField(AutoReacciones)
