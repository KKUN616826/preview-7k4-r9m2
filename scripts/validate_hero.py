"""Validate exported evidence, assets and the assembled hero, without private logs."""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _file_digest(handle):
    """hashlib.file_digest needs Python 3.11; fall back to chunked reads."""
    if hasattr(hashlib, 'file_digest'):
        return hashlib.file_digest(handle, 'sha256')
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1 << 20), b''):
        digest.update(chunk)
    return digest


def validate_hero(content=None):
    data = json.loads((ROOT / 'data/hero-demo.json').read_text())
    if content is None:
        content = (ROOT / 'index.html').read_text()
    embedded = re.search(r'<script id="heroDemoData" type="application/json">(.*?)</script>', content, re.S)
    assert embedded and json.loads(embedded[1]) == data, 'Hero HTML differs from exported evidence'
    events = data['events']
    assert len(events) == 12 and [event['step'] for event in events] == list(range(1, 13))
    assert [event['keyId'] for event in events] == [25, 15, 23, 17, 13, 2, 0, 25, 2, 27, 1, 28]
    assert len({event['snapshot'] for event in events}) == 12, 'Repeated keys need independent screenshots'
    assert len(re.findall(r'class="demo-card"', content)) == 12
    for i, event in enumerate(events):
        assert event['label'] == f'K{event["keyId"] + 1:02d}'
        assert (ROOT / event['snapshot']).is_file()
        assert event['snapshot'] in content
        assert 0 <= event['observe'] < event['observeEnd'] < data['media']['actStart']
        assert data['media']['actStart'] < event['trigger'] < event['release'] < data['media']['duration']
        assert event['arm'] in ('Left', 'Right')
        assert event['triggerStep'] < event['releaseStep']
        assert 0 < event['target'][0] < 1920 and 0 < event['target'][1] < 1080
        assert abs(event['trigger'] - (8 + (event['sourceTrigger'] - 60.5) / 4)) < 1e-6
        if i:
            assert events[i - 1]['observeEnd'] < event['observe']
            assert events[i - 1]['release'] < event['trigger']
    motion = data['motion']
    assert motion['sampleHz'] == 30 and motion['unit'] == 'cm' and motion['referenceFrame'] == 'simulation world'
    assert data['clock']['physicsHz'] == 120 and data['clock']['nativeClockVerified'] is True
    assert data['clock']['releaseSamplePeriodSeconds'] == 10 / 120
    assert data['provenance']['acceptedExpertEpisode'] is False
    assert data['provenance']['fullWorkflowClaim'] is False
    samples = motion['samples']
    assert samples[0][0] <= 8 and samples[-1][0] >= data['media']['duration']
    for index, sample in enumerate(samples):
        assert len(sample) == 3 and all(math.isfinite(value) for value in sample)
        assert all(motion['range'][0] <= height <= motion['range'][1] for height in sample[1:])
        if index:
            assert abs(sample[0] - samples[index - 1][0] - 1 / 120) < 2e-6
    with (ROOT / data['media']['path']).open('rb') as video:
        assert _file_digest(video).hexdigest() == data['media']['sha256']
    presentation, detail = data['presentation'], data['actDetail']
    assert data['version'] == 3
    assert presentation['fps'] == 30 and presentation['playbackRate'] == 0.75
    assert abs(presentation['duration'] - 569 / 30) < 1e-6
    assert presentation['path'] in content
    with (ROOT / presentation['path']).open('rb') as video:
        assert _file_digest(video).hexdigest() == presentation['sha256']
    segments = presentation['segments']
    assert [s['phase'] for s in segments] == ['observe', 'focus', 'reproduce']
    for i, segment in enumerate(segments):
        assert abs(segment['start'] * 30 - round(segment['start'] * 30)) < 1e-6
        assert abs((segment['end'] - segment['start']) * segment['speed'] -
                   (segment['sourceEnd'] - segment['sourceStart'])) < 1e-6
        if i:
            assert segment['start'] == segments[i - 1]['end']
    assert detail['arm'] == events[0]['arm'] == 'Right'
    assert detail['keyId'] == events[0]['keyId'] == 25
    assert 0 < detail['trigger'] < detail['release'] < 4.5
    assert abs(detail['sourceStart'] + detail['trigger'] - events[0]['sourceTrigger']) < 1e-6
    assert abs(detail['sourceStart'] + detail['release'] - events[0]['sourceRelease']) < 1e-6
    assert events[1]['sourceTrigger'] > detail['sourceEnd']
    assert detail['sampleHz'] == 120 and detail['measuredTipHz'] == 30
    assert detail['heightUnit'] == 'cm' and detail['jointUnit'] == 'deg'
    assert len(detail['samples']) == 541 and len(detail['columns']) == 15
    assert 'feedback82.json' in data['provenance']['files']
    for i, sample in enumerate(detail['samples']):
        assert len(sample) == 15 and all(math.isfinite(value) for value in sample)
        assert all(motion['range'][0] <= z <= motion['range'][1] for z in sample[1:3])
        if i:
            assert abs(sample[0] - detail['samples'][i - 1][0] - 1 / 120) < 2e-6
    assert any(abs(row[1] - row[2]) > 0.01 for row in detail['samples']), 'Reference must not replace observations'
    cx, cy, cw, ch = detail['crop']
    ox, oy, ow, oh = detail['outputRectangle']
    assert 0 <= cx < cx + cw <= 1920 and 0 <= cy < cy + ch <= 1080
    for actual, expected in zip(detail['target'], [ox + (events[0]['target'][0] - cx) * ow / cw, oy + (events[0]['target'][1] - cy) * oh / ch]):
        assert abs(actual - expected) < 0.001
    assert detail['crop'] == detail['outputRectangle'] == [0, 0, 1920, 1080]
    assert detail['target'] == events[0]['target']
    hx, hy, hw, hh = detail['highlightRegion']
    assert 0 <= hx < hx + hw <= 1920 and 0 <= hy < hy + hh <= 1080
    assert hx < detail['target'][0] < hx + hw and hy < detail['target'][1] < hy + hh
    transition = presentation['transition']
    assert transition['boundaries'] == [segment['start'] for segment in segments[1:]]
    assert transition['fadeOut'] == transition['fadeIn'] == 0.2
    assert segments[1]['start'] + detail['release'] < transition['boundaries'][1] - transition['fadeOut']
    assert detail['trigger'] > transition['fadeIn']
    assert events[0]['trigger'] - 8 > transition['fadeIn']
    assert 'Single-action focus · Right arm' in content
    assert 'GT target · controller reference' in content
    print('PASS: three-scene edit, isolated contact/release, controller targets and post-step measurements')
    assert 'Simulation demonstration' in content and 'Illustrative memory overlay' in content
    assert 'Recorded simulation heights in world coordinates, in centimeters.' in content
    assert 'class="demo-chart"' in content and 'class="demo-seek"' not in content
    print('PASS: 12 independent screenshots, recorded 30 Hz heights, 120 Hz triggers, release ordering and embedded hero data')


if __name__ == '__main__':
    validate_hero()
