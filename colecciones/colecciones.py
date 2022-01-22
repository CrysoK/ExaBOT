from datetime import datetime as dt
from mongoengine import (
    Document,
    EmbeddedDocument,
    IntField,
    StringField,
    ListField,
    BooleanField,
    DateTimeField,
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


class Respuestas(EmbeddedDocument):
    """Conjunto de mensajes que el bot envía como respuesta a un comando o
    evento."""

    humanos = EmbeddedDocumentListField(MensajeOut)
    bots = EmbeddedDocumentListField(MensajeOut)
    canal = IntField(required=True, default=0)


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


class Usuarios(Document):
    """
    Datos de un usuario que pertenece a múltiples espacios.
    """

    meta = {"collection": "usuarios"}

    _id = IntField(primary_key=True)


class Canales(Document):
    """
    Datos de canales que el bot debe observar constantemente para cumplir con
    ciertas funciones. Los id de los canales son únicos para todo Discord por
    lo que no es necesario el id del espacio al que pertenecen.
    """

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)


class Mensajes(Document):
    """
    Datos de mensajes que el bot debe observar constantemente para cumplir con
    ciertas funciones. Los id de los mensajes son únicos para todo Discord por
    lo que no es necesario el id del espacio ni del canal al que pertenecen.
    """

    _id = IntField(primary_key=True)
    espacio = IntField(required=True)
    canal = IntField(required=True)


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


# def send(*args):
#     return 0


# random = 0
# espacio = Espacios.objects(id=123).first()
# config = espacio.entrada
# bot = True
# if config.canal != 0:
#     # Sí hay configurado canal para todos los mensajes
#     if bot:
#         mensaje = config.bots[random]
#     else:
#         mensaje = config.humanos[random]
#     send(mensaje.texto, mensaje.adjunto, config.canal)
