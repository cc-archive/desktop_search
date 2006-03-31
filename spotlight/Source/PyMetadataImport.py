#
#  PyMetadataImport.py
#  CC_Importer
#
#  Created by Nathan Yergler on 6/2/05.
#  Copyright (c) 2005 Creative Commons. 
#  Licensed under the GNU GPL v2.

import objc
from Foundation import *

import cctagutils

class PyMetadataImport (NSObject):

	# [metadata getMetadataForFile: pathToFile ofType: contentTypeUTI withAttributes: attributes];
	def getMetadataForFile_ofType_withAttributes_(self, filepath, type_uti, attributes):
		NSLog(filepath)
		
		meta = cctagutils.metadata.metadata(filepath)
		claim = meta.getClaim()
		if claim is None:
			# the file does not contain a license claim
			attributes['org_creativecommons_license'] = ['(not licensed)']
		else:
			attributes['org_creativecommons_license'] = [cctagutils.lookup.parseClaim(claim)['license']] 
		
		attributes['kMDItemRecordingYear'] = meta.getYear()
		attributes['kMDItemTitle'] = meta.getTitle()
		attributes['kMDItemAuthors'] = meta.getArtist()
		
		return attributes
		
