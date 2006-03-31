"""cctag library constants."""

__id__ = "$Id$"
__version__ = "$Revision$"
__copyright__ = '(c) 2004, Creative Commons, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

def version():
	v = file('version.txt').read().strip()
	return v
	
TAG_MAP = {
	'UFI':'UFID',
	'BUF':'RBUF',
	'CNT':'PCNT',
	'COM':'COMM',
	'CRA':'AENC',
	'CRM':None, # ('bin','Encrypted meta frame')
	'EQU':'EQU2',
	'ETC':'ETCO',
	'GEO':'GEOB',
	'IPL':'IPLS',
	'LNK':'LINK',
	'MCI':'MCDI',
	'MLL':'MLLT',
	'PIC':'APIC',
	'POP':'POPM',
	'REV':'RVRB',
	'RVA':'RVA2',
	'STC':'SYTC',
	'SLT':'SYLT',
	'TAL':'TALB',
	'TBP':'TBPM',
	'TCM':'TCOM',
	'TCO':'TCON',
	'TCR':'TCOP',
	'TDA':'TDAT',
	'TDY':'TDLY',
	'TEN':'TENC',
	'TIM':'TIME',
	'TKE':'TKEY',
	'TLA':'TLAN',
	'TLE':'TLEN',
	'TMT':'TMED',
	'TP1':'TPE1',
	'TP2':'TPE2',
	'TP3':'TPE3',
	'TP4':'TPE4',
	'TPA':'TPOS',
	'TPB':'TPUB',
	'TOA':'TOPE',
	'TOF':'TOFN',
	'TOL':'TOLY',
	'TOR':'TORY',
	'TOT':'TOAL',
	'TRC':'TSRC',
	'TRD':'TRDA',
	'TRK':'TRCK',
	'TSI':'TSIZ',
	'TSS':'TSSE',
	'TT1':'TIT1',
	'TT2':'TIT2',
	'TT3':'TIT3',
	'TXT':'TEXT',
	'TYE':'TYER',
	'TXX':'TXXX',
	'ULT':'USLT',
	'WAF':'WOAF',
	'WAR':'WOAR',
	'WAS':'WOAS',
	'WCM':'WCOM',
	'WCP':'WCOP',
	'WPM':'WPUB',
	'WXX':'WXXX',
	}

