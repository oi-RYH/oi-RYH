# RYH Community Mine

Preview branch: `codex/game-profile-readme-preview`.

The preview deliberately links unmined blocks to the local help section. It does not create issues. The original workbench banner and project descriptions remain independent of the game.

## Activate after review

Merge into the default branch (`main`) when ready. The workflow's main push trigger renders live links. GitHub issue and scheduled triggers require the workflow on the default branch. The workflow requests only contents and issues write permissions; repository policy and branch protection still apply. Do not disable protections merely for this feature.

Each valid request has the title `mine|LAYER|X|Y`. The workflow scans open requests, persists receipts, commits state and README, pushes, then replies and closes issues. Unrelated or malformed issues are left alone. Only game request issues are processed. An hourly run recovers missed requests; processing time is not guaranteed.

No issue text is interpolated into shell commands. Requests contain a layer number, repeated issue IDs do not score again, and ore is drawn at mining time rather than stored as discoverable hidden state. The queue processes at most 50 requests per run and scans at most 1,000 open issues. This is a casual shared game, not a tamper-proof competition; user cooldowns are not implemented. Public participation creates public issues and game commits.

If a push conflicts with another update, the workflow fails before announcing success. Rerun it on fresh state. Receipts prevent re-awarding already saved requests. A crash between posting a comment and closing an issue is recovered using a bot comment receipt marker.

## Local verification

`python3 -m unittest discover -s scripts -p 'test_*.py' -v`

`python3 scripts/mine.py` renders preview mode and initializes real empty state, without network access. To process live requests the workflow runs `python scripts/mine.py --queue` with `GH_TOKEN`, `GITHUB_REPOSITORY`, and `DEFAULT_BRANCH`. Do not run that command for a local preview.

Block SVG artwork adapted from the user-provided minecraft-readme template. Title/status animation is local SVG with a reduced-motion fallback. The supplied day/night banners and sample personal data are intentionally unused.
