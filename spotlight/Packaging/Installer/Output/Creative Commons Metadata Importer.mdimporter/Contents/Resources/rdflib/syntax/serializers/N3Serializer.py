#$Id$

from rdflib.syntax.serializer import AbstractSerializer

class N3Serializer(AbstractSerializer):

    short_name = "n3"

    def __init__(self, store):
        super(N3Serializer, self).__init__(store)

    def __output(self, stream): pass
        
