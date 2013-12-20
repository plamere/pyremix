import os
import sys
import time
import simplejson as json
import urllib2
from pydub import AudioSegment
import pyen


class Remix(object):

    def __init__(self, api_key = None, cache_dir=".remix-cache", trace=False):
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
        ''' Gets the analysis for a track '''

        if path in self._trid_cache:
            trid = self._trid_cache[path]
        else:
            trid = self._upload(path, type)
            self._save_trid_to_cache(path, trid)

        profile = self._get_profile(trid)
        analysis = self._get_analysis(trid)

        if self._trace:
            print 'bars', len(analysis['bars'])
            print 'beats', len(analysis['beats'])
            print 'tatums', len(analysis['tatums'])
            print 'segments', len(analysis['segments'])

        audio = AudioSegment.from_file(path, type)

        if self._trace:
            print 'frame count', audio.frame_count()
            print 'channels', audio.channels;
            print 'sample width', audio.sample_width
            print 'frame_rate', audio.frame_rate
            print 'frame_width', audio.frame_width
            

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

        return track


    def render(self, l):
        ''' render the given list of quanta into a returned song '''

        out = None
        for q in l:
            audio  = self._get_qaudio(q)
            if out == None:
                out = audio
            else:
                out = out.append(audio, crossfade=0)
        return out

    def q_silence(self, duration):

        q = { }
        q['type'] = 'synthetic';
        q['start'] = 0
        q['duration'] = duration
        q['audio_segment'] = AudioSegment.silent(int(round(duration * 1000)))
        return q

    def q_gain(self, q, volume_change):
        qc = q.copy()
        audio  = self._get_qaudio(qc)
        self._set_qaudio(qc, audio.apply_gain(volume_change))
        return qc

    def q_reverse(self, q):
        qc = q.copy()
        audio  = self._get_qaudio(qc)
        self._set_qaudio(qc, audio.reverse())
        return qc

    def q_combine(self, q1, q2):
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

    def _check_cache_dir(self):
        if self._cache_dir:
            if not os.path.exists(self._cache_dir):
                try:
                    os.makedirs(self._cache_dir)
                except:
                    print "Remix can't create cache at", self._cache_dir, 'performance will be affected'
                    self._cache_dir = None
        else:
            print "No cache directory configured, performance will be affected"

    def print_quanta(self, q):
        print "%s %d s:%.4f dur:%.4f iip:%d" % (q['type'], q['which'], q['start'], q['duration'], q['index_in_parent'])


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
