import mongoengine as me


class News(me.Document):
    title = me.StringField(required=True, min_length=2, max_length=512)
    body = me.StringField(required=True, min_length=2, max_length=2048)
