"""Public owned repositories, ordered by GitHub pushed_at (not metadata edits)."""
from html import escape
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def select(repos, owner):
    eligible = [r for r in repos if not r.get('private') and not r.get('fork')
                and not r.get('archived') and r['name'].lower() != owner.lower()
                and r.get('pushed_at') and r.get('size', 0) > 0]
    eligible.sort(key=lambda r: (r['pushed_at'], r['name']), reverse=True)
    return [dict(name=r['name'], description=r.get('description') or '',
                 language=r.get('language') or '', pushed_at=r['pushed_at'])
            for r in eligible[:3]]

def refresh(owner, root=ROOT):
    repos = []
    for page in range(1, 101):
        request = Request(f'https://api.github.com/users/{quote(owner, safe="")}/repos?type=owner&sort=pushed&direction=desc&per_page=100&page={page}',
                          headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-recent-repos'})
        # The public user endpoint never returns private repositories.
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        repos.extend(batch)
        if len(batch) < 100: break
    else:
        raise RuntimeError('Repository pagination limit exceeded')
    selected = select(repos, owner)
    (root / 'data/recent-repos.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n')
    return selected

def language_badge(language):
    label = language or '언어 정보 없음'
    logos = {
        'C++': ('cplusplus', '7DD3FC'), 'C#': ('dotnet', 'A78BFA'),
        'Python': ('python', 'FACC15'), 'TypeScript': ('typescript', '60A5FA'),
        'JavaScript': ('javascript', 'F7DF1E'), 'Swift': ('swift', 'FB923C'),
        'Java': ('openjdk', 'F89820'), 'C': ('c', 'A8B9CC'),
        'Rust': ('rust', 'DEA584'), 'Go': ('go', '00ADD8'),
        'HTML': ('html5', 'E34F26'), 'CSS': ('css', '663399'),
        'Kotlin': ('kotlin', 'A97BFF'), 'Dart': ('dart', '54C5F8'),
        'Shell': ('gnubash', '89E051'), 'Jupyter Notebook': ('jupyter', 'F37626'),
    }
    # Keep the familiar language logo, but put it on an angular inventory-slot
    # badge using the dirt/workbench palette from the rest of the profile.
    params = {'style': 'for-the-badge', 'color': '241A12'}
    if language in logos:
        params['logo'], params['logoColor'] = logos[language]
    # Shields escapes a literal hyphen by doubling it.
    url = 'https://img.shields.io/badge/' + quote(label.replace('-', '--'), safe='') + '-241A12?' + urlencode(params)
    return f'<img src="{escape(url, quote=True)}" alt="{escape(label, quote=True)}" />'

def cards(repos, owner):
    from inventory_projects import cards as inventory_cards
    return inventory_cards(repos, owner)

def populate(source, root=ROOT):
    from mine import replace
    from inventory_projects import write_inventory
    owner = os.environ.get('GITHUB_REPOSITORY', 'oi-RYH/oi-RYH').split('/')[0]
    repos = json.loads((root / 'data/recent-repos.json').read_text())
    write_inventory(repos, root)
    return replace(source, 'RECENT_REPOS', cards(repos, owner))
