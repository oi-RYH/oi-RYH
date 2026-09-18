import unittest
import xml.etree.ElementTree as ET

from activity_map import contribution_level, render


class ActivityMapTests(unittest.TestCase):
    def calendar(self):
        weeks = []
        for week in range(3):
            weeks.append({'contributionDays': [
                {'date': f'2026-09-{week*7+day+1:02d}', 'weekday': day,
                 'contributionCount': (week + day) % 6}
                for day in range(7)]})
        return {'totalContributions': 42, 'weeks': weeks}

    def test_levels_are_bounded(self):
        self.assertEqual(contribution_level(0, 20), 0)
        self.assertEqual(contribution_level(1, 20), 1)
        self.assertEqual(contribution_level(999, 20), 5)

    def test_svg_is_self_contained_accessible_and_animated(self):
        svg = render(self.calendar(), 'player')
        ET.fromstring(svg)
        self.assertIn("player&#x27;s Minecraft contribution mine: 42 contributions", svg)
        self.assertEqual(svg.count('class="day level-'), 21)
        self.assertNotIn('<text', svg)
        self.assertNotIn('href="http', svg)
        self.assertIn('href="data:image/png;base64,', svg)
        for name in ('stone', 'iron-ore', 'gold-ore', 'diamond-block', 'emerald-block'):
            self.assertIn(name, svg)
        self.assertIn('@keyframes ride', svg)
        self.assertIn('prefers-reduced-motion', svg)
        self.assertIn('id="cart"', svg)
        self.assertIn('class="xp-frame"', svg)


if __name__ == '__main__':
    unittest.main()
