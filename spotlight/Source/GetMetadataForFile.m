//
//  GetMetadataForFile.m
//  CC_Importer
//
//  Created by Nathan Yergler on 6/2/05.
//  Copyright (c) 2005 Creative Commons. 
//  Licensed under the GNU GPL v2.

#import <Foundation/Foundation.h>
#import <AppKit/NSFileWrapper.h>

Boolean GetMetadataForFile(void *thisInterface, NSMutableDictionary *attributes, NSString *contentTypeUTI, NSString *pathToFile)
{
    static BOOL pluginLoaded = NO;
    static Class PyMetadataImport = nil;

	NSBundle *md_bundle = nil;
	NSString *pluginPath = nil;
	NSString *mdPath = nil;
	
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];

    if (!pluginLoaded) {
		NSFileWrapper *bundles = [[NSFileWrapper alloc] init];
		[bundles initWithPath:@"/Library/Spotlight"];

		NSEnumerator *enumerator = [[bundles fileWrappers] objectEnumerator];
		id key;
		
		// check each item and see if this is the bundle
		while ((pluginPath == nil) && (key = [enumerator nextObject])) {
			mdPath = [@"/Library/Spotlight/" stringByAppendingString:[key filename]];
			md_bundle = [NSBundle bundleWithPath:mdPath];
			if (md_bundle == nil) {
				// this wasn't a bundle... try again
				continue;
			}
			
			pluginPath = [md_bundle pathForResource:@"PyMetadataImport"
									ofType:@"plugin"];
		}
	
        NSBundle *pluginBundle = [NSBundle bundleWithPath:pluginPath];
        PyMetadataImport = [pluginBundle classNamed:@"PyMetadataImport"];
        if (!PyMetadataImport) {
            NSLog(@"PyMetadataImport class not found in @%",pluginPath);
        }
        pluginLoaded = YES;
    }

	id metadata = [[PyMetadataImport alloc] init];
	[metadata getMetadataForFile: pathToFile ofType: contentTypeUTI withAttributes: attributes];

    [pool release];

	return TRUE;
}
