import pyremix
import sys

def alt_beats(inpath1, inpath2, outpath):
    '''
        render a new version of the input song that consists
        of the beats in reverse order
    '''
    remixer = pyremix.Remix(trace=True)

    track1 = remixer.analyze_track(inpath1)
    track2 = remixer.analyze_track(inpath2)
    beats1 = track1['analysis']['beats']
    beats2 = track2['analysis']['beats']

    out = []
    for b1, b2 in zip(beats1, beats2):
        if b1:
            out.append(b1)
        if b2:
            out.append(b2)

    audio = remixer.render(out)
    audio.export(outpath, format="mp3")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python %s input1.mp3 imput2.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 3:
            outpath = sys.argv[3]
        alt_beats(sys.argv[1], sys.argv[2], outpath)
