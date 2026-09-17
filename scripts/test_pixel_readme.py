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
        (self.root / 'data').mkdir()
        shutil.copy(ROOT / 'data/recent-repos.json', self.root / 'data/recent-repos.json')

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
        self.assertIn('<picture><img', result)
        for path in (self.root/'assets/text').glob('*.svg'): ET.parse(path)

    def test_plain_text_is_not_clickable_but_intended_links_remain_clickable(self):
        renderer = __import__('pixel_readme').PixelText(self.root)
        result = renderer.render('일반 글씨\n\n[블로그](https://example.com)\n\n'
                                 '# <img src="assets/headings/workbench.svg" alt="제목">')
        self.assertRegex(result, r'<picture><img src="assets/text/[^"]+"[^>]+alt="일반 글씨"></picture>')
        self.assertRegex(result, r'\[<img src="assets/text/[^"]+"[^>]+alt="블로그">\]\(https://example.com\)')
        self.assertIn('<picture><img src="assets/headings/workbench.svg" alt="제목"></picture>', result)

    def test_repository_description_has_exactly_two_lines_and_is_clamped(self):
        source = ('<!-- RECENT_REPOS:START -->\n'
                  '<table><tr><td width="33%" valign="top">\n'
                  '<p data-repo-description>한 줄 설명</p>\n'
                  '<p data-repo-description>아주 긴 저장소 설명을 여러 번 반복해서 두 줄보다 훨씬 길게 만듭니다. '
                  '아주 긴 저장소 설명을 여러 번 반복합니다.</p>\n'
                  '</td></tr></table>\n'
                  '<!-- RECENT_REPOS:END -->')
        # This test bypasses repository population while exercising the marker.
        renderer = __import__('pixel_readme').PixelText(self.root)
        result = renderer.render(source)
        assets = re.findall(r'src="(assets/text/[^\"]+)"', result)
        self.assertEqual(len(assets), 2)
        for asset in assets:
            svg = (self.root / asset).read_text()
            self.assertIn('height="48"', svg)
        self.assertEqual((self.root / assets[0]).read_text().count('<g transform="translate('), 1)
        self.assertEqual((self.root / assets[1]).read_text().count('<g transform="translate('), 2)

if __name__ == '__main__': unittest.main()
