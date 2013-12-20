import remix
import sys

def breverse(inpath, outpath):
    '''
        reverse each beat of audio
    '''
    remixer = remix.Remix(trace=True)
    track = remixer.analyze_track(inpath)
    beats = track['analysis']['tatums']
    out = []
    for b in beats:
        out.append(remixer.q_reverse(b))
    audio = remixer.render(out)
    audio.export(outpath, format="mp3")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        breverse(sys.argv[1], outpath)
