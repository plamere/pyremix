import pyremix
import sys

def reverse(inpath, key, outpath):
    '''
        render a new version of the input song that consists
        of the beats in reverse order
    '''
    remixer = pyremix.Remix(trace=True)
    track = remixer.analyze_track(inpath)
    beats = track['analysis']['beats']
    beats.sort(key=lambda beat:beat[key])
    beats.reverse()
    audio = remixer.render(beats)
    audio.export(outpath, format="mp3")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s input.mp3 key [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 3:
            outpath = sys.argv[3]
        reverse(sys.argv[1], sys.argv[2], outpath)
