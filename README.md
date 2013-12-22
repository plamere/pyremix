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

### Reverse

Reversing a song, beat by beat:

	import pyremix
	
    remixer = pyremix.Remix()
    track = remixer.analyze_track("audio/BadRomanceClip.mp3")
    beats = track['analysis']['beats']
    beats.reverse()
    remixer.render(beats).export("backwards.mp3")
    
Here's the input (BadRomanceClip.mp3): 

<audio src="http://static.echonest.com/pyremix/audio/BadRomanceClip.mp3" controls/>. 

Here's the output (backwards.mp3):

<audio src="http://static.echonest.com/pyremix/audio/backwards.mp3" controls/> 
    
    
### One

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

Here's some sample output (beat1_romance.mp3):

<div><audio src="http://static.echonest.com/pyremix/audio/beat1_romance.mp3" controls/></div>

### Blip

In this example, we add a blip to every bar, beat or tatum:

'''python
	import pyremix
    remixer = pyremix.Remix()

	type = 'beats' # could be 'bars', 'sections', 'tatums' or 'segments'
    track = remixer.analyze_track(inpath)
    blip =  remixer.q_from_file("examples/sounds/blip_high.wav", "wav")
    song = []
    for q in track['analysis'][type]:
        song.append(remixer.q_combine(q, blip))
    remixer.render(song).export(outpath)
 '''

Example output:
    
<audio src="http://static.echonest.com/pyremix/audio/blip_romance.mp3" controls/> 

## Documentation

See the [Full API documentation](http://static.echonest.com/pyremix/docs/pyremix.html)

## Caching
pyremix keeps a local cache of track analyses. This eliminates the need for pyremix to re-upload audio.  By default the cache is kept in ~/.remix-cache            
## Dependencies
pyremix depends on the following libraries

 - [pyen](https://github.com/plamere/pyen) - a simple, thin, un-opinionated python client for The Echo Nest API 
 - [pydub](https://github.com/jiaaro/pydub/) - Manipulate audio with a simple and easy high level interface 
 
 
## TODO
There's still lots to do:

  - Add DIRAC support for time stretching and pitch shifting
  - Fill out the examples to include all examples from remix
  - Improve the docs
 
 