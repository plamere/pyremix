# pyremix

This is a refactoring of The Echo Nest's remix library. The goal of this refactoring is to:

 - eliminate much of the cruft that has accumulated over the years
 - have a better method for caching and reusing analyses
 - consolidate/simplify and fully document the API
 - eliminate dependencies on numpy and scipy that can make it difficult to install
 - reduce the overall footprint of the package so it can be distributed via pypi
 
## Example
Here's the classic 'one.py' that makes a new song that consists of just the first beats of every bar of the source song.

    import remix
    import sys

    def one(inpath, outpath):
        remixer = remix.Remix()
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
            
            
            
## TODO
There's still lots to do:

  - Add DIRAC support for time stretching and pitch shifting
  - Fill out the examples to include all examples from remix
  - Improve the docs
 
 