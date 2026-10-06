"""
other_games_trainer.py  -  the CS2 model, trained for the other esports PandaScore covers.

It runs cs_trainer.py unchanged (same team + player Elo, rosters, form, head-to-head, logistic model),
only pointed at another game's PandaScore matches. Round scores are used where PandaScore has them
(Valorant, Rainbow Six); other games simply skip the margin-of-victory step.

Run:   python other_games_trainer.py valorant          # -> models/valorant.json + models/valorant.js
       python other_games_trainer.py r6 --months 18
       python other_games_trainer.py ow --demo         # offline pipeline check
Games: valorant, r6, ow, rl, cod, mlbb
The Esports Intel site reads models/<game>.js from this repo.
"""
import json, os, sys

import cs_trainer as T

GAMES = {"valorant": "valorant", "r6": "r6siege", "ow": "ow", "rl": "rl", "cod": "codmw", "mlbb": "mlbb"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in GAMES:
        sys.exit("usage: python other_games_trainer.py <" + "|".join(GAMES) + "> [cs_trainer options]")
    game = sys.argv.pop(1)
    slug = GAMES[game]
    os.makedirs("models", exist_ok=True)
    T.CACHE_DIR = f"cache_{game}"
    out = f"models/{game}.json"
    if os.environ.get("PANDASCORE_TOKEN"):
        T.TOKEN = os.environ["PANDASCORE_TOKEN"]
    base_get = T.ps_get

    def ps_get(path, *a, **k):  # every /csgo/... call goes to this game's matches instead
        return base_get(path.replace("/csgo/", f"/{slug}/", 1), *a, **k)

    T.ps_get = ps_get
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
