import pyremix
import sys

def blip(inpath, type, outpath):
    '''
        a simple version of more cowbell. Merely
        adds a cowbell to the most confident beats
    '''
    confidence_threshold = .0

    remixer = pyremix.Remix(trace=True)

    track = remixer.analyze_track(inpath)
    bell =  remixer.q_from_file("sounds/blip_high.wav", "wav")

    song = []

    for q in track['analysis'][type]:
        if q['confidence'] >= confidence_threshold:
            song.append(remixer.q_combine(q, bell))
        else:
            song.append(q)

    audio = remixer.render(song)
    audio.export(outpath, format="mp3")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python %s input.mp3 [type] [out.mp3]' % (sys.argv[0],)
    else:
        type = 'beats'
        outpath = 'out.mp3'
        if len(sys.argv) > 2:
            type = sys.argv[2]
        if len(sys.argv) > 3:
            outpath = sys.argv[3]
        blip(sys.argv[1], type, outpath)
