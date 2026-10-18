"""
other_games_trainer.py  -  the CS2 model, trained for the other esports PandaScore covers.

It runs cs_trainer.py unchanged (same team + player Elo, rosters, form, head-to-head, logistic model),
only pointed at another game's PandaScore matches. Round scores are used where PandaScore has them
(Valorant, Rainbow Six); other games simply skip the margin-of-victory step.

Run:   python other_games_trainer.py valorant          # -> models/valorant.json + models/valorant.js
       python other_games_trainer.py valorant --tune   # retune this game's settings -> tune_valorant.json (as tune.py does for CS2)
       python other_games_trainer.py r6 --months 18
       python other_games_trainer.py ow --demo         # offline pipeline check
Games: valorant, r6, ow, rl, cod, mlbb
The Esports Intel site reads models/<game>.js from this repo.
"""
import json, os, sys

import cs_trainer as T

DEFAULTS = {"K_TEAM": 32.0, "K_PLAYER": 20.0, "L2": 1.0, "CAP": 0.85}
GAMES = {"valorant": "valorant", "r6": "r6siege", "ow": "ow", "rl": "rl", "cod": "codmw", "mlbb": "mlbb"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in GAMES:
        sys.exit("usage: python other_games_trainer.py <" + "|".join(GAMES) + "> [cs_trainer options]")
    game = sys.argv.pop(1)
    slug = GAMES[game]
    os.makedirs("models", exist_ok=True)
    T.CACHE_DIR = f"cache_{game}"
    out = f"models/{game}.json"
    if not T.TOKEN and os.environ.get("PANDASCORE_TOKEN"):  # same token as cs_trainer.py; the secret only if that is empty
        T.TOKEN = os.environ["PANDASCORE_TOKEN"]
    base_get = T.ps_get

    def ps_get(path, *a, **k):  # every /csgo/... call goes to this game's matches instead
        return base_get(path.replace("/csgo/", f"/{slug}/", 1), *a, **k)

    T.ps_get = ps_get
    # each game has its own tuned settings: start from the defaults (not CS2's tune.json), then this game's file
    T.apply_tune(DEFAULTS)
    T.TUNE_FILE = f"tune_{game}.json"
    if os.path.exists(T.TUNE_FILE):
        T.apply_tune(json.load(open(T.TUNE_FILE, encoding="utf-8")).get("settings"))
    if "--tune" in sys.argv:
        sys.argv.remove("--tune")
        import tune
        tune.T = T
        if "--out" not in sys.argv:
            sys.argv += ["--out", T.TUNE_FILE]
        if "--odds" not in sys.argv:
            sys.argv += ["--odds", f"odds_log_{game}.json"]
        tune.main()
        return
    if "--out" not in sys.argv:
        sys.argv += ["--out", out]
    if "--odds" not in sys.argv:
        sys.argv += ["--odds", f"odds_log_{game}.json"]  # no market log for these games (yet)
    T.main()
    model = json.load(open(out, encoding="utf-8"))
    model["game"] = game
    blob = json.dumps(model, separators=(",", ":"))
    json.dump(model, open(out, "w", encoding="utf-8"), separators=(",", ":"))
    open(f"models/{game}.js", "w", encoding="utf-8").write("window.MODEL_REMOTE=" + blob + ";")
    print(f"wrote models/{game}.js")


if __name__ == "__main__":
    main()
