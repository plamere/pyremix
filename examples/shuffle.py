import remix
import random
import sys

def reverse(inpath, outpath):
    '''
        render a new version of the input song that consists
        of the beats in reverse order
    '''
    remixer = remix.Remix(trace=True)
    track = remixer.analyze_track(inpath)
    beats = track['analysis']['beats']
    random.shuffle(beats)
    audio = remixer.render(beats)
    audio.export(outpath, format="mp3")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        reverse(sys.argv[1], outpath)
