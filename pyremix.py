import os
import sys
import time
import simplejson as json
import urllib2
from pydub import AudioSegment
import pyen


'''
    A simplified refactoring of The Echo Nest's remix library.
'''
class Remix(object):

    def __init__(self, api_key = None, cache_dir="~/.remix-cache", trace=False):
        """ Creates a new remixer

        Args:
            api_key: the Echo Nest API key. If not set, look
                     for one in the ECHO_NEST_API_KEY environment variable

            cache_dir: directory for analysis cache

            trace: trace salient events

        """

        self._en = pyen.Pyen(api_key)
        self._trace = trace
        self._cache_dir = cache_dir
        self._check_cache_dir()
        self._trid_cache = self._load_trid_cache()


    def analyze_track(self, path, type='mp3'):
        ''' Gets the analysis for a track 

            Args:

                path (string): pathname of the audio file to be analyzed
                type (string, optional): indicator of the type of the audio

            Returns:
                track: the track as a dictionary, containing the detailed analysis
                   of the audio

        '''

        path = os.path.abspath(path)

        if path in self._trid_cache:
            trid = self._trid_cache[path]
        else:
            trid = self._upload(path, type)
            self._save_trid_to_cache(path, trid)

        profile = self._get_profile(trid)
        analysis = self._get_analysis(trid)

        if self._trace:
            print "Analysis:  sections:%d bars:%d beats:%d tatums:%d segments:%d" % (
                len(analysis['sections']), len(analysis['bars']), len(analysis['beats']),
                len(analysis['tatums']), len(analysis['segments']))

        audio = AudioSegment.from_file(path, type)

        if self._trace:
            print "Audio:     frames:%d channels:%d samplewidth:%d framerate:%d framewidth:%d" % (
                audio.frame_count(), audio.channels, audio.sample_width, 
                audio.frame_rate, audio.frame_width)
            

        track = {
            'trid' : trid,
            'analysis' : analysis,
            'profile' : profile,
            'audio' : audio
        }

        self._connect_quanta(track, 'sections')
        self._connect_quanta(track, 'bars')
        self._connect_quanta(track, 'beats')
        self._connect_quanta(track, 'tatums')
        self._connect_quanta(track, 'segments')

        self._connect_quanta_with_children(track, 'sections', 'bars')
        self._connect_quanta_with_children(track, 'bars', 'beats')
        self._connect_quanta_with_children(track, 'beats', 'tatums')

        self._connect_overlapping_segments(track, 'sections')
        self._connect_overlapping_segments(track, 'bars')
        self._connect_overlapping_segments(track, 'beats')
        self._connect_overlapping_segments(track, 'tatums')

        self._annotate_quanta_from_overlapping_segments(track, 'sections')
        self._annotate_quanta_from_overlapping_segments(track, 'bars')
        self._annotate_quanta_from_overlapping_segments(track, 'beats')
        self._annotate_quanta_from_overlapping_segments(track, 'tatums')

        return track


    def render(self, l):
        ''' render the given list of quanta into a returned song 

            Args:
                l (list): a list of quanta to be rendered into a song

            Returns:
                a song (as a pydub.AudioSegment)

        '''

        out = None
        for q in l:
            audio  = self._get_qaudio(q)
            if out == None:
                out = audio
            else:
                out = out.append(audio, crossfade=0)
        return out


    def q_from_file(self, path, type):
        ''' represents an audio file as a quantum 

            Args:
                path(string): path name of the file
                type(string): the type of the audio

            Returns:
                dict: the quantum
        '''
        q = { }
        q['type'] = 'synthetic';
        q['start'] = 0
        q['audio_segment'] = self._audio_from_file(path, type)
        q['duration'] = q['audio_segment'].duration_seconds
        return q

    def q_silence(self, duration):
        ''' return a quanta of silence for the given duration 

            Args:
                duration(float) : the duration of the silence

            Returns:
                dict: the quantum
        '''
        q = { }
        q['type'] = 'synthetic';
        q['start'] = 0
        q['duration'] = duration
        q['audio_segment'] = AudioSegment.silent(int(round(duration * 1000)))
        return q

    def q_gain(self, q, volume_change):
        ''' Adjust the volume of a quanta, volume_change is in DBs

            Args:
                volume_change(float) : the amount of volume change in DBs

            Returns:
                dict: the quantum
        '''
        qc = q.copy()
        audio  = self._get_qaudio(qc)
        self._set_qaudio(qc, audio.apply_gain(volume_change))
        return qc

    def q_reverse(self, q):
        ''' reverse the audio within a quanta

            Returns:
                dict: the quantum
        '''
        qc = q.copy()
        audio  = self._get_qaudio(qc)
        self._set_qaudio(qc, audio.reverse())
        return qc

    def q_resize(self, q, factor):
        ''' resizes the duration of the quantum by the given factor. Note that
            no time stretching is done. 

            Args:
                factor(float) : new quantum duration is old['duration'] * factor

            Returns:
                dict: the quantum
        '''
        qc = q.copy()
        qc['duration'] = qc['duration'] * factor
        if factor > 1 and 'audio_segment' in qc:
            del qc['audio_segment']
        return qc

    def q_volume_ramp(self, q, to_gain, start_time, end_time = None):
        ''' changes the volume to the given gain

            Args:
                to_gain(float): change in DBs
                start_time(float): starting time for the ramp
                end_time(float): ending time for the ramp

            Returns:
                dict: the quantum
        '''
        qc = q.copy()
        audio  = self._get_qaudio(qc)
        if end_time == None:
            end_time = qc['duration']
        end_time = int(end_time * 1000) 
        audio = audio.fade(to_gain, start=int(start_time * 1000), end=end_time)
        self._set_qaudio(qc, audio)
        return qc


    def q_time_stretch(self, q, duration):
        ''' stretches (or shrinks) a quantum to the given time

            Args:
                duration(float): the duration of the new quantum

            Returns:
                dict: the quantum
        '''
        # not implemented yet
        return q

    def q_pitch_shift(self, q, factor):
        ''' shifts the pitch of a quantum up (positive) or down (negative)
            percentage.  

            Args:
                factor(float): the amount of change of pitch (2.0 will double the pitch)

            Returns:
                dict: the quantum
        ''' 
        # not implemented yet
        return q

    def q_combine(self, q1, q2):
        ''' combine 2 quanta

            Args:
                q1(dict): a quantum
                q2(dict): a quantum

            Returns:
                dict: the combined quantum
        '''
        qc = q1.copy()
        audio1  = self._get_qaudio(q1)
        audio2  = self._get_qaudio(q2)
        audio3 = audio1.overlay(audio2)
        self._set_qaudio(qc, audio3)
        return qc

    def _connect_quanta(self, track, type):
        qlist = track['analysis'][type]

        for i, q in enumerate(qlist):
            q['type'] = type;
            q['audio'] = track['audio']
            q['end'] = q['start'] + q['duration']
            q['which'] = i;
            q['index_in_parent'] = -1;
            q['parent'] = None;
            q['children'] = [];
            q['overlapping_segments'] = [];


            if i > 0:
                q['prev'] = qlist[i-1]
            else:
                q['prev'] = None
            
            if i <  len(qlist) - 1:
                q['next'] = qlist[i+1]
            else:
                q['next'] = None

    def _connect_quanta_with_children(self, track, parent_type, child_type):
        plist = track['analysis'][parent_type]
        clist = track['analysis'][child_type]

        cur_child  = clist[0]
        for p in plist:
            while cur_child and cur_child['start'] < p['end']:
                if cur_child['start'] >= p['start']:
                    cur_child['parent'] = p
                    cur_child['index_in_parent'] = len(p['children'])
                    p['children'].append(cur_child)
                cur_child = cur_child['next']


    def _connect_overlapping_segments(self, track, type):
        plist = track['analysis'][type]
        slist = track['analysis']['segments']

        cur_seg  = slist[0]
        p = plist[0]
        while p:
            while cur_seg and p and cur_seg['start'] <= p['end']:
                if cur_seg['end'] > p['start']:
                    p['overlapping_segments'].append(cur_seg)
                    p = p['next']
                else:
                    cur_seg = cur_seg['next']

    def _connect_overlapping_segments(self, track, type):
        plist = track['analysis'][type]
        for p in plist:
            p['overlapping_segments'] = self._find_overlapping(track, p, 'segments')


    def _find_overlapping(self, track, tgt, type):
        results = []
        for q in track['analysis'][type]:
            if q['start'] > tgt['end']:
                break
            if q['end'] < tgt['start']:
                continue
            results.append(q)
        return results

    def _annotate_quanta_from_overlapping_segments(self, track, type):
        for q in track['analysis'][type]:
            if len(q['overlapping_segments']) == 0:
                q['loudness_min'] = -60
                q['loudness_max'] = -60
            else:
                q['loudness_min'] = 0
                q['loudness_max'] = -60
                for seg in q['overlapping_segments']:
                    if seg['loudness_start'] < q['loudness_min']:
                        q['loudness_min'] = seg['loudness_start']
                    if seg['loudness_max'] > q['loudness_max']:
                        q['loudness_max'] = seg['loudness_max']

    def _load_trid_cache(self):
        cache = {}
        if self._cache_dir:
            dir = os.path.join(self._cache_dir, 'directory.txt')
            if os.path.exists(dir):
                f = open(dir)
                for line in f:
                    trid, path = line.strip().split(' <sep> ')
                    cache[trid] = path
                    cache[path] = trid
                f.close()
        return cache

    def _save_trid_to_cache(self, path, trid):
        if self._cache_dir:
            dir = os.path.join(self._cache_dir, 'directory.txt')
            f = open(dir, 'a')
            print >>f, trid, '<sep>', path
            f.close()

    def _get_qaudio(self, q):
        if not 'audio_segment' in q:
            audio = q['audio']
            start_frame = int(round(q['start'] * audio.frame_rate))
            end_frame = start_frame + int(round(q['duration'] * audio.frame_rate))
            qaudio = audio.get_sample_slice(start_frame, end_frame)
            q['audio_segment'] = qaudio
            if False:
                print 'qa', q['start'], q['duration'], start_frame, end_frame, len(qaudio)
        return q['audio_segment']

    def _set_qaudio(self, q, audio):
        q['audio_segment'] = audio

    def _get_profile(self, trid, refresh=False):
        path = os.path.join(self._cache_dir, trid + '.profile.json')
        if refresh or not os.path.exists(path):
            response = self._en.get('track/profile', id=trid, bucket=['audio_summary'])
            profile = response['track']
            self._save_to_cache(path, profile)
        else:
            profile = self._load_from_cache(path)
        return profile

    def _get_analysis(self, trid):
        path = os.path.join(self._cache_dir, trid + '.analysis.json')
        if not os.path.exists(path):
            profile = self._get_profile(trid, True)
            analysis_url = profile['audio_summary']['analysis_url']
            f = urllib2.urlopen(analysis_url)
            js = f.read()
            f.close()

            analysis = json.loads(js)
            self._save_to_cache(path, analysis)
        else:
            analysis = self._load_from_cache(path)
        return analysis

    def _upload(self, path, type):
        if self._trace:
            print 'uploading', path, type
        f = open(path, 'rb')
        response = self._en.post('track/upload', track=f, filetype=type)
        f.close()

        trid = response['track']['id']
        response = self._wait_for_analysis(trid)
        if self._trace:
            print
            print 'trid', trid
        return trid


    def _save_to_cache(self, path, dict):
        f = open(path,'w')
        print >>f, json.dumps(dict)
        f.close()

    def _load_from_cache(self, path):
        f = open(path,'r')
        js = f.read()
        f.close()
        return json.loads(js)

    def _wait_for_analysis(self, trid):
        if self._trace:
            print 'checking status of', trid,

        while True:
            response = self._en.get('track/profile', id=trid, bucket=['audio_summary'])
            if response['track']['status'] <> 'pending':
                return response['track']
            else:
                if self._trace:
                    print ".",
            time.sleep(1)
        return None

    def _audio_from_file(self, path, type):
        return AudioSegment.from_file(path, type)

    def _check_cache_dir(self):
        if self._cache_dir:
            self._cache_dir = os.path.expanduser(self._cache_dir)
            if not os.path.exists(self._cache_dir):
                try:
                    os.makedirs(self._cache_dir)
                except:
                    print "Remix can't create cache at", self._cache_dir, 'performance will be affected'
                    self._cache_dir = None
        else:
            print "No cache directory configured, performance will be affected"

    def print_quanta(self, q):
        print "%s %d s:%.4f dur:%.4f iip:%d" % (q['type'], q['which'], q['start'], q['duration'], q['index_in_parent']),
        if q['type'] != 'segments':
            print " children:%d  ovlps: %d maxl %d minl %d" % (len(q['children']), len(q['overlapping_segments']), 
                q['loudness_max'], q['loudness_min'])
        else:
            print


def _test(path):
    remix = Remix(trace=True)
    print 'loading beats'
    track = remix.analyze_track(path)
    out = []

    print 'building beats'
    for i, beat in enumerate(track['analysis']['beats']):
        if i % 4 == 0:
            out.append(beat)

    print 'rendering beats'
    audio = remix.render(out)

    print 'exporting beats'
    audio.export("out.mp3", format="mp3")

if __name__ == '__main__':
    _test(sys.argv[1])
