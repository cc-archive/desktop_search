#!/usr/bin/env python2.3
#
#  setup.py
#  CC_Importer
#
#  Created by Nathan Yergler on 6/3/05.
#  Copyright (c) 2005 Creative Commons. All rights reserved.
#

from distutils.core import setup
import py2app

# generates a PyObjC plugin which the Obj-C stub can load @ run time
setup(
    plugin = ['PyMetadataImport.py']
)   