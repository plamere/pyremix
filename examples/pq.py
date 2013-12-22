
import pyremix
import sys

def pq(inpath, type):
    '''
        prints out the quanta of the given type
    '''
    remixer = pyremix.Remix(trace=True)
    track = remixer.analyze_track(inpath)
    for q in track['analysis'][type]:
        remixer.print_quanta(q)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [type]' % (sys.argv[0],)
    else:
        type = 'beats'
        if len(sys.argv) > 2:
            type = sys.argv[2]
        pq(sys.argv[1], type)
