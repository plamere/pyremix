import pyremix
import sys

def separated_segments(inpath, outpath):
    '''
        separate ever segment by short stretch of silence
    '''
    remixer = pyremix.Remix(trace=True)

    track = remixer.analyze_track(inpath)
    silence = remixer.q_silence(.33)
    out = []
    for i, q in enumerate(track['analysis']['segments']):
        out.append(q)
        out.append(silence)

    audio = remixer.render(out)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        separated_segments(sys.argv[1], outpath)
