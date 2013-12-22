import pyremix
import sys

def adjust_speed(inpath, factor, outpath):
    '''
        adjusts the speed of the given song, beat by beat
    '''

    remixer = pyremix.Remix(trace=True)

    track = remixer.analyze_track(inpath)

    song = []

    for q in track['analysis']['beats']:
        song.append(remixer.q_resize(q, factor))

    audio = remixer.render(song)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [factor] [out.mp3]' % (sys.argv[0],)
    else:
        factor = .8
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            factor = float(sys.argv[2])
        if len(sys.argv) > 3:
            outpath = sys.argv[3]
        adjust_speed(sys.argv[1], factor, outpath)
