import random
import sys
import pyremix

def shuffle_bars(inpath, outpath):
    '''
        reorder the beats in each bar so that they are in
        descending loudness order
    '''
    remixer = pyremix.Remix(trace=True)
    track = remixer.analyze_track(inpath)

    song = []
    for bar in track['analysis']['bars']:
        beats = bar['children']
        random.shuffle(beats)
        song.extend(beats)

    audio = remixer.render(song)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        shuffle_bars(sys.argv[1], outpath)
