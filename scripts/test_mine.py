import copy
from pathlib import Path
import random
import unittest
import xml.etree.ElementTree as ET
import mine

class MineTests(unittest.TestCase):
    def test_invalid_input_does_not_mutate(self):
        for title in ['mine|1|0|0$(id)', 'mine|1|6|0', 'mine|1|0|3', 'mine|0|0|0', 'hello']:
            state = mine.initial_state()
            before = copy.deepcopy(state)
            self.assertIsNone(mine.play(state, title, 'player', 1))
            self.assertEqual(before, state)

    def test_duplicate_issue_and_block(self):
        state = mine.initial_state()
        result = mine.play(state, 'mine|1|0|0', 'player', 1, random.Random(1))
        self.assertEqual(result, mine.play(state, 'mine|1|0|0', 'player', 1))
        mine.play(state, 'mine|1|0|0', 'other', 2)
        self.assertEqual(state['miners']['player']['blocks'], 1)
        self.assertNotIn('other', state['miners'])

    def test_one_successful_mine_per_user_per_utc_day(self):
        state = mine.initial_state()
        first = mine.play(state, 'mine|1|0|0', 'player', 1, random.Random(1), '2026-09-18')
        blocked = mine.play(state, 'mine|1|1|0', 'player', 2, random.Random(1), '2026-09-18')
        self.assertIn('획득', first)
        self.assertEqual(blocked, '오늘은 이미 채굴했습니다. UTC 자정 이후 다시 도전해주세요.')
        self.assertIsNone(state['grid'][0][1])
        next_day = mine.play(state, 'mine|1|1|0', 'player', 3, random.Random(1), '2026-09-19')
        self.assertIn('획득', next_day)
        self.assertEqual(state['miners']['player']['blocks'], 2)

    def test_failed_attempt_does_not_consume_daily_mine(self):
        state = mine.initial_state()
        mine.play(state, 'mine|1|0|0', 'first', 1, random.Random(1), '2026-09-18')
        failed = mine.play(state, 'mine|1|0|0', 'second', 2, random.Random(1), '2026-09-18')
        success = mine.play(state, 'mine|1|1|0', 'second', 3, random.Random(1), '2026-09-18')
        self.assertIn('이미 누군가', failed)
        self.assertIn('획득', success)

    def test_rollover_rejects_old_links(self):
        state = mine.initial_state()
        for y in range(mine.HEIGHT):
            for x in range(mine.WIDTH):
                index = 1 + y * mine.WIDTH + x
                mine.play(state, f'mine|1|{x}|{y}', f'player-{index}', index)
        self.assertEqual(state['layer'], 2)
        self.assertEqual(state['grid'], mine.new_grid())
        mine.play(state, 'mine|1|0|0', 'late-player', 100)
        self.assertNotIn('late-player', state['miners'])

    def test_preview_live_and_markers(self):
        text = (mine.ROOT / 'README.md').read_text()
        state = mine.initial_state()
        preview = mine.render(text, state)
        self.assertNotIn('/issues/new?', preview)
        live = mine.render(text, state, live=True)
        self.assertEqual(live.count('/issues/new?'), mine.WIDTH*mine.HEIGHT)
        self.assertIn('mine%7C1%7C0%7C0', live)
        self.assertEqual(live.count('assets/mine-grid/cell-'), mine.WIDTH*mine.HEIGHT)
        self.assertIn('data-theme="gold-leaf-neungwha"', (mine.MINE_SLOT_DIR / 'cell-1-1.svg').read_text())
        for path in mine.MINE_SLOT_DIR.glob('cell-*.svg'):
            ET.parse(path)
        self.assertIn('<p align="center">', live)
        with self.assertRaises(ValueError):
            mine.render('missing markers', state)

    def test_render_idempotent(self):
        text = (mine.ROOT / 'README.md').read_text()
        state = mine.initial_state()
        first = mine.render(text, state)
        self.assertEqual(first, mine.render(first, state))

if __name__ == '__main__':
    unittest.main()
