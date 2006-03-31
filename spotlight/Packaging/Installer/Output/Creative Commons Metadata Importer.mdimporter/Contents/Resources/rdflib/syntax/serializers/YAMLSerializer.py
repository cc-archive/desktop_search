#$Id$

from rdflib.syntax.serializer import AbstractSerializer

class YAMLSerializer(AbstractSerializer):

    short_name = "yaml"

    def __init__(self, store):
        super(YAMLSerializer, self).__init__(store)

    def serialize(self, stream=None): pass
