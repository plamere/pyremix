import pyremix
import sys

def echo(inpath, outpath):
    '''
        echos each beat with a quieter version of the beat
    '''
    remixer = pyremix.Remix(trace=True)

    track = remixer.analyze_track(inpath)
    out = []
    for i, beat in enumerate(track['analysis']['beats']):
        out.append(beat)
        out.append(remixer.q_gain(beat, -5))
    audio = remixer.render(out)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        echo(sys.argv[1], outpath)
