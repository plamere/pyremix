import remix
import sys

def one(inpath, outpath):
    '''
        render a new version of the input song that consists
        of just the first beat of every bar
    '''
    remixer = remix.Remix(trace=True)

    track = remixer.analyze_track(inpath)
    beats = []
    for i, beat in enumerate(track['analysis']['beats']):
        if beat['index_in_parent'] == 0:
            beats.append(beat)
    audio = remixer.render(beats)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        one(sys.argv[1], outpath)
