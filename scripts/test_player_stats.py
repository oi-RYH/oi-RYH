import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from player_stats import fetch_stats, render


class PlayerStatsTests(unittest.TestCase):
    def stats(self):
        return {
            'login': 'player', 'public_repos': 14, 'stars': 7, 'followers': 9,
            'year_contributions': 456, 'last_active': '2026-09-17',
            'current_repo': 'Dawn',
            'languages': {'JavaScript': 700, 'Python': 200, 'Swift': 100},
        }

    def test_inventory_is_accessible_self_contained_and_complete(self):
        svg = render(self.stats())
        ET.fromstring(svg)
        self.assertIn('player Minecraft player inventory', svg)
        self.assertIn('14 public repositories, 7 stars, 9 followers, 456 contributions', svg)
        self.assertNotIn('<text', svg)
        self.assertIn('href="data:image/jpeg;base64,', svg)
        self.assertEqual(svg.count('href="http'), 0)
        self.assertEqual(svg.count('class="slot"'), 10)
        self.assertIn('prefers-reduced-motion', svg)
        self.assertIn('aria-label="안경을 쓰고 곡괭이와 맥북을 든 스티브"', svg)

    def test_missing_languages_render_empty_slots(self):
        stats = self.stats()
        stats['languages'] = {}
        svg = render(stats)
        self.assertEqual(svg.count('class="item"'), 0)

    @patch('player_stats.fetch_calendar')
    @patch('player_stats.api')
    def test_profile_repository_is_not_a_quest_or_language_source(self, api, calendar):
        calendar.return_value = {'totalContributions': 3, 'weeks': [
            {'contributionDays': [{'date': '2026-09-17', 'contributionCount': 3}]}]}
        profile = {'name': 'player', 'fork': False, 'archived': False,
                   'pushed_at': '2026-09-17', 'stargazers_count': 50}
        project = {'name': 'project', 'fork': False, 'archived': False,
                   'pushed_at': '2026-09-16', 'stargazers_count': 2}
        api.side_effect = [
            {'followers': 4}, [profile, project], {'Python': 100},
        ]
        stats = fetch_stats('player', 'token')
        self.assertEqual(stats['public_repos'], 2)
        self.assertEqual(stats['current_repo'], 'project')
        self.assertEqual(stats['stars'], 2)
        self.assertEqual(stats['languages'], {'Python': 100})


if __name__ == '__main__':
    unittest.main()
