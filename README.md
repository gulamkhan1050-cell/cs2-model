# cs2-model
## Versions and the weekly update

The app shows its version (**v1.1**, **v1.2**, ...) and a **What's new** list under the title.

| Workflow | When | Does |
|---|---|---|
| `weekly release` | every 3 days at 03:15 UTC (08:45 India), or by hand | `tune.py` re-checks team K, player K, ridge strength and the per-map cap on the newest results (writes `tune.json`, which `cs_trainer.py` reads) → retrains → `release.py` writes the next version and its notes (`release.json`) → `build.py` → publishes `app.shell.html` |

- The APK's start page is `loader.html`: online it opens the published `app.shell.html` (so a new version needs no new APK), offline the last page it saw or the copy inside the APK.
- Each match card shows the **Esports Intel** grade (A / B, locked 1 minute before the start, won / lost after) from `https://esports-intel.onrender.com/api/grades`, and whether it agrees with this model.
- Settings change only when clearly better on the newest 20% of games (log-loss gain of 0.001 or more).
