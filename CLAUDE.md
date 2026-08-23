# Judged Awards Ranking

Ranks FIRST Robotics Competition (FRC) teams by how many times they have won a
given **judged** award, using data from The Blue Alliance (TBA).

The primary target for development and testing is the **Excellence in Engineering
Award** (`award_type: 21`). The end goal is to produce this ranking for *every*
judged award in FRC, so prefer award-type-parameterized code over anything
hardcoded to a single award.

## Layout

| Path | Purpose |
| --- | --- |
| `data_pulling_script.py` | One-shot fetch: pulls all team keys for a season, then every award for every team; writes `AwardData.json`. |
| `AwardData.json` | Cached TBA award data (git-ignored, ~9.6 MB). |
| `.env` | Holds `TBA_API_KEY`. Git-ignored and denied to Claude reads. |
| `.env.example` | Committed template for `.env`. |

## Setup

```bash
echo "TBA_API_KEY=your_key_here" > .env
```

Get a read key at https://www.thebluealliance.com/account. The script loads
`.env` with a small built-in parser (no `python-dotenv` dependency) and exits
with a clear message if the key is missing.

Only dependency is `requests`.

## Refreshing the data

```bash
python data_pulling_script.py
```

This makes ~3,700+ API calls (one per team) and takes a while. `AwardData.json`
is the cache — **do not re-run the pull just to iterate on ranking logic.** Read
the existing JSON instead. Bump `CURRENT_SEASON` in the script to change which
season's team roster is enumerated (award history returned per team is all-time
regardless).

## Data shape

`AwardData.json` is `{team_key: [award, ...]}`, keyed like `"frc1"`, `"frc254"`:

```json
{
  "frc1": [
    {
      "award_type": 17,
      "event_key": "1998mi",
      "name": "Quality",
      "recipient_list": [{"awardee": null, "team_key": "frc1"}],
      "year": 1998
    }
  ]
}
```

Because the file is keyed by team, counting wins per team is a straight tally —
each award appears once in each winning team's list, so there is no
cross-team deduplication to do.

## Critical: count on `award_type`, never on `name`

`name` is free text entered per event and is wildly inconsistent. Award type 21
alone appears under 13 different names across history:

- `Excellence in Engineering Award`
- `Excellence in Engineering Award sponsored by Delphi`
- `Engineering Excellence Award sponsored by Delphi`
- `Best Climbing Bot (Engineering Excellence)`
- `Endurance Award`
- ...and more

Sponsor names change over the decades, districts invent their own titles, and
some names have stray trailing whitespace. `award_type` is TBA's stable
numeric enum and is the only reliable grouping key. Any string matching on
`name` will silently undercount.

Watch for the inverse trap too: the substring "Engineering" also matches
`award_type: 9` (Engineering Inspiration) and `23` (Excellence in Design),
which are entirely different awards.

## Judged vs. non-judged awards

TBA's award list mixes judged awards with competition-performance results and
one-off novelty awards. The ranking should cover judged awards only. Notable
**non-judged** types to exclude include:

- `1` District/Regional Event Winner, `2` Event Finalist
- `14` Highest Rookie Seed, `39` #1 Seed, `59` High Score
- `40` Incredible Play, `43` Best Offensive Round, `47` Outstanding Defense
- `68` Wildcard
- `74`/`75` Skills Competition Winner/Finalist

Some award types go to an **individual, not a team** — `3` Woodie Flowers
Finalist, `4` Dean's List Finalist, `5` Volunteer of the Year. These have a
non-null `awardee` in `recipient_list`. Decide deliberately whether a team
"won" these; they are arguably out of scope for a team ranking.

There are 78 distinct `award_type` values (ids run 0–83, with gaps) present in the current data, many with
only a handful of occurrences (novelty awards invented by a single event). A
long tail of tiny counts is expected, not a bug.

## Conventions

- Award history spans 1992–present, so year-scoped rankings ("wins since 2015")
  are a likely follow-on feature; keep year filtering easy to thread through.
- `event_key` is prefixed with the year (`2019txcmp`). Championship events
  contain `cmp`; district championships contain `dcmp`. Useful if wins should
  ever be weighted by event level.
- Secrets go in `.env` only. Never inline an API key in a script or commit one.
