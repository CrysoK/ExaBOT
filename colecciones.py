# DEPENDENCIAS ################################################################

from datetime import datetime as dt
from mongoengine import (
    # Clases padre
    Document,
    EmbeddedDocument,
    # Campos
    IntField,
    StringField,
    BooleanField,
    URLField,
    DateTimeField,
    ListField,
    DynamicField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
)

# EMBEDDED ####################################################################


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


# MODERACIÓN ##################################################################


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


class Kicks(Document):
    """
    Datos relevantes de un ban.
    """

    meta = {"collection": "kicks"}

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    # Infractor
    usuario = IntField(required=True)
    # Responsable
    autor = IntField(required=True)
    motivo = StringField(default="Motivo no indicado")
    evidencia = EmbeddedDocumentListField(MensajeIn)
    fecha = DateTimeField(required=True, default=dt.utcnow)


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


# USUARIOS ####################################################################


class Usuarios(Document):
    """
    Datos de un usuario que pertenece a múltiples espacios.
    """

    meta = {"collection": "usuarios"}

    _id = IntField(primary_key=True)


# ESPACIOS ####################################################################


A_TODOS = 0
SOLO_A_HUMANOS = 1
SOLO_A_BOTS = 2


class Saludo(EmbeddedDocument):
    """Mensaje usado en las funciones de 'Saludos'"""

    tipo = IntField(required=True, default=A_TODOS)
    canal = IntField(required=True)
    texto = StringField(required=True)


class Espacios(Document):
    """
    Datos relacionados a un espacio en particular.
    """

    meta = {"collection": "espacios"}

    _id = IntField(primary_key=True)
    # `casos` indica la cantidad de warns, kicks, bans, etc. Se incrementa cada
    # vez que se registra uno para asignarle un id único.
    casos = IntField(required=True, default=0)
    entrada = EmbeddedDocumentListField(Saludo)
    salida = EmbeddedDocumentListField(Saludo)
    kick = EmbeddedDocumentListField(Saludo)
    ban = EmbeddedDocumentListField(Saludo)
    # Cómo implementar los canales con restricciones?


# CANALES #####################################################################


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


# MENSAJES ####################################################################


class Mensajes(Document):
    """
    Datos de mensajes que el bot debe observar constantemente para cumplir con
    ciertas funciones. Los id de los mensajes son únicos para todo Discord por
    lo que no es necesario el id del espacio ni del canal al que pertenecen.
    """

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    canal = IntField(required=True)


# EXTRA #######################################################################


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


class FBPosts(Document):
    """
    Datos de un post de Facebook. Lo ideal es que estén ordenados por espacio,
    luego por página y luego por fecha.
    """

    meta = {"collection": "fb_posts"}

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    pagina = IntField(required=True)
    fecha = DateTimeField(required=True)
