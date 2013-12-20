import remix
import sys

def swap23(inpath, outpath):
    '''
        render a new version of the input song that consists
        of the beats in reverse order
    '''
    remixer = remix.Remix(trace=True)
    track = remixer.analyze_track(inpath)
    beats = track['analysis']['beats']

    out = []
    for b in beats:
        if b['index_in_parent'] == 2 and b['next']:
            out.append(b['next'])
        elif b['index_in_parent'] == 3 and b['prev']:
            out.append(b['prev'])
        else:
            out.append(b)
    audio = remixer.render(out)
    audio.export(outpath, format="mp3")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [out.mp3]' % (sys.argv[0],)
    else:
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            outpath = sys.argv[2]
        swap23(sys.argv[1], outpath)
