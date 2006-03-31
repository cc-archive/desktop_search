"""
rdfdict.py

A generic wrapper for RDFlib which provides a dictionary-like interface to
blocks of RDF with common subjects.  Also provides a utility wrapper,
rdfStore, for parsing and generating RDF.

(c) 2003-2004, Nathan R. Yergler
Licensed under the GNU GPL2
"""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2003-2004, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

# enable generators
from __future__ import generators

# import some basic support structure
import sys
import xml.sax.xmlreader
import cStringIO
import sets

# import RDF handling facilities
from rdflib.TripleStore import TripleStore
from rdflib.BNode import BNode
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef

class AmbiguousKeyError(KeyError):
    """Raised when there are multiple values for a given key."""
    
class StringInputSource(xml.sax.xmlreader.InputSource):
    """
    StringInputSource: helper source to allow SAX parsing of a string;
    wraps string in appropriate superclass and emulates file-like interface.
    """
    def __init__(self, sourceString):
        # call the superclass constructor
        xml.sax.xmlreader.InputSource.__init__(self)

        # store the input string
        self.__source = cStringIO.StringIO(sourceString)
        self.setByteStream(self.__source)

class rdfDict:
    """
    Provides a dictionary-like wrapper around a set of RDF triples with a
    common subject.  In addition to the standard dictionary interface
    provides convenience methods for manipulating the triples.
    """
    def __init__(self, subject, rdfStore=None):
        """
        Creates a new rdfDict given the particular subject and an optional
        TripleStore (rdfStore).  If no TripleStore is provided, creates a
        new one.
        """

        # store the subject
        self.subject = subject

        # store or create the triple store
        if rdfStore is None:
            self.store = TripleStore()
        else:
            self.store = rdfStore

    def __str__(self):
        """
        Return the string representation of this instance using an algorithm
        inspired by the Dublic Core dumb-down method.
        """

	output_str = ''
        pairs = []
	type_item = None
        
        for key in self:
	    if (key.find("#type") != -1): 
	      type_item = key
	    else:
	      pairs.append((key, self.getAll(key)))

	output_str = str(self.getFirst(type_item)) + ": "

	for pair in pairs:
	   output_str = '%s %s: %s;' % (output_str,
                                        str(pair[0]),
                                        ", ".join([str(n) for n in pair[1]]) ) 

	return output_str

    def about(self):
        """
        Return the subject used to create the instance (usually equivalent
        to rdf:about.
        """
        return self.subject

    def __getvalues(self, key):
        """
        Returns a list of values for a particular key; coerces BNodes to
        rdfDicts and mangles Literals with language attributes (if available).
        """

        values = [ n for n in self.store.objects(subject=self.subject,
                                                 predicate=key)
                   ]

        result = []
        
        for value in values:
            if (isinstance(value, BNode)):
                # coerce to rdfDict
                result.append(rdfDict(value, self.store))
            else:
                result.append(value)

        return result
                            
    def __getitem__(self, key):
        """
        Return the object described in RDF with a subject of self.subject
        and a predicate of key.  If more than one match is found, raises
        an AmbiguousKeyError.
        """

        result = self.__getvalues(key)

        if (len(result) == 0):
            # no item was found, throw an exception
            raise KeyError()
        elif (len(result) > 1):
            # check if there is more than one option
            raise AmbiguousKeyError()
        else:
            # otherwise return object value
            return result[0]

    def getFirst(self, key):
        """
        Returns the first object having the predicate key.  If no match is
        found returns None.
        """

        if ( (self.subject, URIRef(key), None) in self.store):
            return self.__getvalues(key)[0]
        else:
            return None
        
    def getAll(self, key):
        """
        Returns a list of objects which have a predicate of key.  The list
        may be empty or contain only a single element.
        """

	return self.__getvalues(key)

    def __setitem__(self, key, value):
        """
        Adds an RDF triple of the values (self.subject, key, value); any
        objects with the same subject/predicate are replaced.
        """

        if (self.subject, key, none) in self.store:
            del self[key]

        self.store.add( (self.subject, key, value) )
        
    def add (self, key, value):
        """
        Adds an RDF triple consisting of the subject, key and value.
        """
        
        self.store.add( (self.subject, key, value) )
        
    def addAll (self, key, values):
        """
        Adds the list of objects in values with the same subject and predicate.
        """
        
        for value in values:
            self.add (key, value)
            
    def __len__(self):
        """
        Returns the number of predicate-object pairs associated with the
        subject self.subject.
        """

        return len(self.store)

    def __delitem__(self, key):
        """
        Removes all items with the given key.
        """

        if (self.subject, key, None) in self.store:
            self.store.remove( (self.subject, key, None) )
        else:
            raise KeyError()

    def remove (self, key, value):
        """
        Removes a specific key-value pair.
        """
        
        self.store.remove( (self.subject, key, value) )

    def __iter__(self):
        """
        Returns an iterator over the unique keys (predicates)
        for the given subject.
        """

        return iter(sets.Set(self.store.predicates(subject=self.subject)))

    iterkeys = __iter__

    def __contains__(self, key):
        """
        Returns true if the given key appears as a predicate of the subject.
        """

        return ( (self.subject, key, None) in self.store )

class rdfStore:
    """
    Provides RDF parsing and output functions for CC license and work
    definitions.
    """
    
    def __init__(self):
        # initialize the TripleStore for managing RDF
        self.store = TripleStore()
        
    def parse(self, rdf):
        """
        Parse the given String, rdf, into it's component triples.
        """

        self.store.parse( StringInputSource (rdf) )

    def subjects(self):
        """A generator which successivly returns each subject contained in
        the store, wrapped in an instance of rdfDict."""

        for subject in self.store.subjects():
            yield rdfDict(subject, store=self.store)
        
    def output(self):
        """
        Return a string containing the RDF representation of the
        licenses and works."""

        if self.store is not None:
            rdf = cStringIO.StringIO()
            self.store.serialize(stream=rdf)
            return rdf.getvalue()
        else:
            return ""

    __str__ = output

    def append(self, newItem):
        """
        Adds a new work or license to the RDF store.
        """

        # make sure the stores aren't the same
        if (newItem.store is not self.store):

            # add each triple from the newItem's store to this store
            for triple in newItem.store.triples():
                self.store.add(triple)
            
    
