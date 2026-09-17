import unittest
from recent_repos import select, cards

class RecentReposTests(unittest.TestCase):
    def test_selection_uses_push_time_and_excludes_ineligible_repos(self):
        def repo(name, pushed, **kwargs):
            return dict(name=name, pushed_at=pushed, size=1, **kwargs)
        repos = [repo('owner', '2026-10-01'), repo('fork', '2026-10-01', fork=True),
                 repo('secret', '2026-10-01', private=True), repo('old', '2026-10-01', archived=True),
                 repo('one', '2026-01-01'), repo('four', '2026-04-01'),
                 repo('three', '2026-03-01'), repo('two', '2026-02-01')]
        self.assertEqual([r['name'] for r in select(repos, 'owner')], ['four', 'three', 'two'])

    def test_repository_metadata_is_escaped(self):
        html = cards([dict(name='demo', description='<script>alert(1)</script>',
                           language=None, pushed_at='2026-09-17T00:00:00Z')], 'owner')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('https://github.com/owner/demo', html)
        self.assertIn('언어 정보 없음', html)

    def test_cards_have_fixed_description_hook_and_minecraft_badge(self):
        html = cards([dict(name='demo', description='short', language='JavaScript',
                           pushed_at='2026-09-17T00:00:00Z')], 'owner')
        self.assertIn('<p data-repo-description>short</p>', html)
        self.assertIn('style=for-the-badge', html)
        self.assertIn('logo=javascript', html)
        self.assertIn('241A12', html)
        self.assertIn('업데이트 · 2026-09-17', html)

if __name__ == '__main__': unittest.main()
