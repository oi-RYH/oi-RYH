import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
import mine
from pixel_readme import ROOT, build

class PixelReadmeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'assets/fonts').mkdir(parents=True)
        shutil.copy(ROOT / 'assets/fonts/neodgm.ttf', self.root / 'assets/fonts/neodgm.ttf')

    def test_live_mine_survives_pixel_conversion_and_score_update(self):
        source = (ROOT / 'README.source.md').read_text()
        state = mine.initial_state()
        state['grid'][0][0] = {'ore': 'stone', 'user': 'player'}
        state['miners']['player'] = {'blocks': 1, 'score': 1}
        state['totals']['stone'] = 1
        first = build(mine.render(source, state, live=True), self.root)
        self.assertEqual(first.count('/issues/new?'), 17)
        self.assertIn('](https://github.com/player)', first)
        self.assertIn('alt="채굴 완료"', first)
        self.assertEqual(first.count('<details'), source.count('<details'))
        state['miners']['player']['score'] = 50
        second = build(mine.render(source, state, live=True), self.root)
        self.assertIn('alt="50"', second)
        files = {str(p.relative_to(self.root)) for p in (self.root/'assets/text').glob('*.svg')}
        self.assertEqual(files, set(re.findall(r'src="(assets/text/[^\"]+)"', second)))
        for path in files: ET.parse(self.root/path)
        self.assertEqual(second, build(mine.render(source, state, live=True), self.root))

    def test_xml_escaping_and_link_preservation(self):
        text = '<details><summary>A &amp; B</summary>\n[Blog ↗](https://example.com)\n</details>'
        result = build(text, self.root)
        self.assertIn('](https://example.com)', result)
        self.assertIn('alt="A &amp; B"', result)
        for path in (self.root/'assets/text').glob('*.svg'): ET.parse(path)

if __name__ == '__main__': unittest.main()
