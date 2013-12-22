import pyremix
import sys

def overlay(inpath, outpath):
    '''
        overlays each beat with the next beat
    '''
    remixer = pyremix.Remix(trace=True)

    track = remixer.analyze_track(inpath)
    out = []
    for i, beat in enumerate(track['analysis']['beats']):
        print i, 'of', len(track['analysis']['beats'])
        if beat['next']:
            out.append(remixer.q_combine(remixer.q_gain(beat, -7), remixer.q_gain(beat['next'], -5)))
        else:
            out.append(beat)

    audio = remixer.render(out)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        overlay(sys.argv[1], outpath)
