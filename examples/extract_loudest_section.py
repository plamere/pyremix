import pyremix
import sys

def extract_loudest(inpath, outpath):
    ''' extracts the loudest section
    '''
    remixer = pyremix.Remix(trace=True)
    track = remixer.analyze_track(inpath)

    loudest = None
    for section in track['analysis']['sections']:
        if loudest == None or section['loudness'] > loudest['loudness']:
            loudest = section
    remixer.render([loudest]).export(outpath)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        extract_loudest(sys.argv[1], outpath)
