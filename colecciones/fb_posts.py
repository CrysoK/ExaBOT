from mongoengine import (
    Document,
    IntField,
    DateTimeField,
)


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
