# pyremix

This is a refactoring of The Echo Nest's remix library. The goal of this refactoring is to:

 - eliminate much of the cruft that has accumulated over the years
 - have a better method for caching and reusing analyses
 - consolidate/simplify and fully document the API
 - eliminate dependencies on numpy and scipy that can make it difficult to install
 - reduce the overall footprint of the package so it can be distributed via pypi
 
This is still very much an experimental version. You probably want the real remix
which you can find on [github](http://echonest.github.io/remix/). 

** Note that this library is not an official Echo Nest library **
 
## Examples


Reversing a song, beat by beat:

	import pyremix
	
    remixer = pyremix.Remix()
    track = remixer.analyze_track("audio/BadRomanceClip.mp3")
    beats = track['analysis']['beats']
    beats.reverse()
    remixer.render(beats).export("backwards.mp3")
    
Here's the input:

   <audio src="audio/BadRomanceClip.mp3">
    
Here's the output:

   <audio src="audio/BadRomanceClip.mp3">
    
    

Here's the classic 'one.py' that makes a new song that consists of just the first beats of every bar of the source song.

    import pyremix

    def one(inpath, outpath):
        remixer = pyremix.Remix()
        track = remixer.analyze_track(inpath)
        
        beats = []
        for i, beat in enumerate(track['analysis']['beats']):
            if beat['index_in_parent'] == 0:
                beats.append(beat)
        remixer.render(beats).export(outpath)

More examples can be found in the [examples](https://github.com/plamere/pyremix/tree/master/examples) directory in the Github repository.

In this example, we add a blip to every bar, beat or tatum:

	import pyremix
    remixer = pyremix.Remix()

	type = 'beats' # could be 'bars', 'sections', 'tatums' or 'segments'
    track = remixer.analyze_track(inpath)
    blip =  remixer.q_from_file("sounds/blip_high.wav", "wav")
    song = []
    for q in track['analysis'][type]:
        song.append(remixer.q_combine(q, blip))
    remixer.render(song).export(outpath)

            
## TODO
There's still lots to do:

  - Add DIRAC support for time stretching and pitch shifting
  - Fill out the examples to include all examples from remix
  - Improve the docs
 
 