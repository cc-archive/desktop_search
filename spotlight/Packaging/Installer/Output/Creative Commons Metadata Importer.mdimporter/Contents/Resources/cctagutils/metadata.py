"""Classes and functions to support embedding metadata in a music file;
contains the abstract class which allows extensions to be implemented for
OGG, etc.
"""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

# use the bundled version of PyTagger, which contains our fixes.
import tagger
import eyeD3
import os
import cctagutils.const as const

class AudioMetadata:
    def __init__(self, filename):
        self.filename = filename

    def getTitle(self):
        raise NotImplementedError()

    def getArtist(self):
        raise NotImplementedError()

    def getYear(self):
        raise NotImplementedError()

    def getClaim(self):
        raise NotImplementedError()

    def setClaim(self, claim):
        raise NotImplementedError()
    
    def embed(self, license, verification, year, holder):
        """Embed a license claim in the audio file."""
        raise NotImplementedError()

    def isWritable(self):
        """Returns true if the user has permission to change the metadata."""
        raise NotImplementedError()
    
class Mp3Metadata(AudioMetadata):
    def __init__(self, filename):
        AudioMetadata.__init__(self, filename)
        self.__open(filename)

    def __open(self, filename=None):
        if filename is not None:
            self.filename = str(filename)

        # create a handle for ID3v2
        self.__tag = eyeD3.Tag()
        try:
            self.__tag.link(self.filename)
        except eyeD3.tag.TagException, e:
            if "2.2" in e.msg:
                print 'aieee!'
                self.__tag = None
            else:
                raise

    def _getFrame(self, fids):
        """Returns the first frame whose ID is contained in the tuple fids.
        Returns None if the frame identifiers do not exist."""

        if self.__tag is None:
            return None

        for frame in self.__tag.frames:
            if frame.header.id in fids:
                return frame

        return None

    def _getFrameData(self, fids):

        # retrieve the frame
        frame = self._getFrame(fids)

        if frame is not None:
			if isinstance(frame, eyeD3.frames.DateFrame):
				return frame.getYear()
			elif isinstance(frame, eyeD3.frames.TextFrame):
				return frame.text
			else:
				return frame.data
        
        return None
    
    def getTitle(self):
        return (self.__tag and self.__tag.getTitle()) or "";

    def getArtist(self):
        return (self.__tag and self.__tag.getArtist()) or "";

    def getYear(self):
        return self._getFrameData(('TYE', 'TYER', 'TDRC')) or ''

    def getClaim(self):
        return self._getFrameData(('TCR', 'TCOP')) or ''
    
    def _needsUpgrade(self):
        """Returns True if a file has ID3 tags of v2.2."""
        if self.__tag is None:
            return True
        elif (self.__tag and len(self.__tag.frames) > 0):
           return ((self.__tag.frames[0].header.majorVersion >= 2) and 
                   (self.__tag.frames[0].header.minorVersion >= 3))
        else:
           # either no ID3 information or no frames; 
           # in either case, no upgrade is neccessary
           return False

    def upgrade(self):
        """Upgrades a file's ID3 tags from ID3v2.2 to ID3v2.3."""

        # open the file using tagger
        self.__v2 = tagger.id3v2.ID3v2(self.filename,
                                       tagger.constants.ID3_FILE_MODIFY)

        # retrieve the existing frames
        oldframes = {}
        for frame in self.__v2.frames:
            oldframes[frame.fid] = (frame.rawdata, frame.length)
            
        # re-open the file for writing
        self.__v2 = tagger.id3v2.ID3v2(self.filename,
                                       mode=tagger.constants.ID3_FILE_NEW,
                                       version=2.3)
        
        # rewrite each frame
        for fid in oldframes:
            if fid not in const.TAG_MAP or const.TAG_MAP[fid] is None:
                # no mapping for this tag
                print "Field can not be converted from 2.2 to 2.3: ", fid
                continue

            newframe = self.__v2.new_frame(fid=const.TAG_MAP[fid])
            newframe.rawdata, newframe.length = oldframes[fid]
            
            newframe.parse_field()

            self.__v2.frames.append(newframe)

        self.__v2.commit()

    
    def _addId3v1(self):
        """Checks for the existance of ID3v1 data in the specified file;
        if it does not exist, generates data from the ID3v2 tags.
        """

        if self.__hasV1:
            return

        self.__v1.songname = self.getTitle()
        self.__v1.artist = self.getArtist()
        self.__v1.year = self.getYear()

        # save the changes
        self.__v1.commit()

        # reload our v1 handle
        self.__v1 = tagger.id3v1.ID3v1(self.filename,
                                       tagger.constants.ID3_FILE_MODIFY)
        
        self.__hasV1 = True

    def __clearTcop(self):
        for f in self.__tag.frames:
            if f.header.id == 'TCOP':
               del f

    def setClaim(self, claim):

        # check if an upgrade to 2.3 is needed before embedding
        if (self._needsUpgrade()):
            # update tags to ID3v2.3
            self.upgrade()

        # reopen the file (in case of 2.2)
        self.__open()
        print self.__tag

        # set the TCOP frame
        self.__clearTcop()
        header = eyeD3.frames.FrameHeader()
        header.id = 'TCOP'
        header.compressed = 0
        tcop = eyeD3.frames.TextFrame(header, text=unicode(claim))

        self.__tag.frames.append(tcop)
        self.__tag.update()

    def embed(self, license, verification, year, holder):
        
        # first generate the embedded license claim str
        claim = "%s %s. Licensed to the public under %s verify at %s" % (
            year, holder, license, verification )

        self.setClaim(claim)
        
        # add ID3v1 if necessary
        # self._addId3v1()

    def isWritable(self):
        """Returns true if the user has permission to change the metadata."""
        return os.access(self.filename, os.W_OK)
    
class OggMetadata(AudioMetadata):
    pass

meta_handlers = {'mp3':Mp3Metadata,
                 'ogg':OggMetadata,
                 }
                
def metadata(filename):
    """Returns the appropriate instance for the detected filetype of
    [filename].  The returned instance will be a subclass of the
    AudioMetadata class."""

    # XXX right now we do stupid name-based type detection; a future
    # improvment might actually look at the file's contents.
    ext = filename.split('.')[-1].lower()
    if ext in meta_handlers:
        return meta_handlers[ext](filename)
    else:
        # fall back to AudioMetadata, which will raise NotImplementedErrors
        # as necessary
        return AudioMetadata(filename)

