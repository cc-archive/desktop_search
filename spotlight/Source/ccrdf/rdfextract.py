"""
rdfextract.py

A pluggable class for extracting RDF from blocks of text.  By default uses
a simple regex for finding RDF; can be extended with any number of other
function for specialized processing.

(c) 2004, Nathan R. Yergler
Licensed under the GNU GPL2
"""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2004, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import urllib2
import urlparse
import re
import sets

import rdfdict

def null_extractor(text, url):
    """This is a sample extractor with no functionality; it exists in the
    source for the purpose of documenting the extractor function signature.

    An extractor function takes a single parameter, text, and returns a list
    of RDF blocks extracted from the text.  If no RDF is found, an empty
    list should be returned.
    """
    return []

def string_extractor(text, url):
    """
    Extracts RDF segments from a block of text using simple string
    methods; for fallback only.
    """

    START_TAG = '<rdf:rdf'
    END_TAG = '</rdf:rdf>'

    lower_text = text.lower()

    matches = []
    startpos = 0

    startpos = lower_text.find(START_TAG, startpos)
    while startpos > -1:
      endpos = lower_text.find(END_TAG, startpos)
      
      if endpos > -1:
         matches.append(text[startpos:endpos+len(END_TAG)])

      startpos = lower_text.find(START_TAG, endpos)

    return matches

def regex_extractor(text, url):
    """
    Extracts RDF segments from a textblock; returns a list of strings.
    """
    # compile the RegEx for extracting RDF
    rdf_regex = re.compile("<rdf:rdf.*?>.*?</rdf:rdf>",
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)

    # extract the RDF bits from the incoming text
    matches = []
    text = text.strip()

    try:
       return rdf_regex.findall(text)
    except:
       return []

def link_extractor(text, url):
    """Extracts metadata stored in linked files specified by
    <link rel="meta" ...> as in:
    <link rel="meta" type="application/rdf+xml"
    href="/en/wiki/wiki.phtml?title=Main_Page&action=creativecommons">
    """

    results = []
    
    # extract the list of link tags
    link_regex = re.compile("<link .*?>",
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    rel_regex = re.compile('rel="meta"',
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    href_regex = re.compile('(href=["\'])(.*?)(["\'])',
                            re.IGNORECASE)
    
    # extract the RDF bits from the incoming text
    matches = []
    text = text.strip()

    links = link_regex.findall(text)

    # check if each link has the correct relationship
    for link in links:
        isrel = rel_regex.search(link)
        if isrel:
            # extract the href
            href = href_regex.search(link)
            if href:
                rdf_href = urlparse.urljoin(url, href.group(2))

		# handle possible HTML escaping
		rdf_href = rdf_href.replace('&amp;', '&')

                # retrieve the href and check for RDF
                results = results + \
                          RdfExtractor().extractRdfText(
                    retrieveUrl(rdf_href), url=rdf_href)
    
    return results

def href_extractor(text, url):
    """Extracts metadata stored in linked files specified by
    <a rel="license" href="..." >
    """

    results = []
    
    # extract the list of link tags
    link_regex = re.compile("<a .*?>",
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    rel_regex = re.compile('rel="license"',
                           re.IGNORECASE|re.DOTALL|re.MULTILINE)
    href_regex = re.compile('(href=["\'])(.*?)(["\'])',
                            re.IGNORECASE)
    
    # extract the RDF bits from the incoming text
    matches = []
    text = text.strip()

    links = link_regex.findall(text)

    # check if each link has the correct relationship
    for link in links:
        isrel = rel_regex.search(link)
        if isrel:
            # extract the href
            href = href_regex.search(link)
            if href:
                rdf_href = urlparse.urljoin(url, href.group(2))

                # retrieve the href and check for RDF
                results = results + \
                          RdfExtractor().extractRdfText(
                    retrieveUrl(rdf_href), url=rdf_href)
    
    return results


# ------------------------------------------------------------------

class RdfExtractor:
    """A pluggable class for extracting RDF from blocks of text."""
    
    def __init__(self, default_extractors = [regex_extractor,
                                             string_extractor,
                                             link_extractor,
                                             href_extractor]):
        """default_extractors contains the list of extractors to use;
        this list can be mutated after instantiation through the extractors
        property. """
        
        self.extractors = default_extractors

    def extractRdfText(self, textblock, url=None):
        """Pass textblock through each extractor in sequence and return
        a list of RDF blocks extracted."""
        
        rdf_blocks = []
        
        for func in self.extractors:
            rdf_blocks = rdf_blocks + func(textblock, url)

        result = list(sets.Set([n.strip() for n in rdf_blocks]))
        # print result
        
        return result

    def extractRdf(self, textblock, url=None):
        """Pass textblock through each extractor in sequence and return
        a list of rdfDict objects."""

        rdf_blocks = self.extractRdfText(textblock, url)

        for block in rdf_blocks:
            store = rdfdict.rdfStore()
            store.parse(block)

            yield store

# ------------------------------------------------------------------
# convenience functions

def retrieveUrl(url):
    """Returns the document contained at [url]."""
    
    headers = {'User-Agent':'ccRdf/Python 2.3'}
    request = urllib2.Request(url, headers=headers)
    
    resource = urllib2.urlopen(request)

    result =  "".join(resource.readlines())
    return result


    
