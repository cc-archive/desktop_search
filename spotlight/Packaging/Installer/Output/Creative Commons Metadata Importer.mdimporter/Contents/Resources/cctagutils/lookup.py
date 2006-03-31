"""Support functions for verification of embedded license claims."""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import ccrdf
import ccrdf.rdfextract as rdfextract

import cctagutils.rdf
from cctagutils.metadata import metadata

def parseClaim(claim):
    results = {}

    vtext = 'verify at '
    vloc = claim.find(vtext)
    if vloc != -1:
            results['verify at'] = claim[vloc+len(vtext):].strip()
            claim = claim[:vloc]

    ltext = "licensed to the public under "
    lloc = claim.lower().find(ltext)
    if lloc != -1:
            results['license'] = claim[lloc+len(ltext):].strip()
            claim = claim[:lloc]

    results['copyright'] = claim.strip()

    return results

def lookup(filename):
    """Returns True of False if the embedded claim can be verified."""
    
    if verify(filename) > 0:
        return True
    else:
        return False
    
def verify(filename):
    """Extracts license claim information from a file and verifies it.
    Returns the following status codes:
    1     Verified
    0     No RDF
    -1    Work information not found (possible SHA1 mismatch)
    -2    Verification license does not match claim.
    """

    status = 0
    
    claim = metadata(filename).getClaim()
    if claim is None:
        raise cctag.exceptions.NotLicensedException
    
    fileinfo = parseClaim(claim)
    fileinfo['sha'] = 'urn:sha1:%s' % cctag.rdf.fileHash(filename)

    verifyRdf = rdfextract.RdfExtractor().extractRdfText(
        rdfextract.retrieveUrl(fileinfo['verify at'])
        )

    # check if we found any RDF at all, and update the status code
    if len(verifyRdf) > 0:
        status = -1

    # check each block of RDF
    #  (a verification page may also have it's own license RDF embedded)
    for block in verifyRdf:
        # parse/validate the RDF
        verifyCc = ccrdf.ccRdf()
        verifyCc.parse(block)

        # for each work in the RDF block...
        for work in verifyCc.works():
            
            # if the subject matches...
            if work.subject == fileinfo['sha']:
                # we found the work information;
                # only one reason left to not verify
                status = -2
                
                # we found the work, now make sure the license matches
                for license in work.licenses():
                    if license == fileinfo['license']:
                        return 1

    # either the file wasn't found, or the license didn't match
    return status
