# 3-minute walkthrough: Device Fleet Reliability

A timed script for a Loom recording of about 3 minutes (screen plus camera bubble, 1080p). Say it in your own words; the lines are a guide, not a teleprompter.

**Open these tabs before you press record:** README, docs/data_profile.md, dbt/models, results/survival.md, GitHub Actions.

| Time | On screen | What to say |
|---|---|---|
| 0:00–0:20 | Portfolio card, then the README title | Which device models fail most, how does failure change with age, and how many units should we replace next quarter? On 30.6 million real drive-days from Backblaze's 351,000-drive fleet, this answers all three with confidence intervals. |
| 0:20–0:45 | README intro and the Data section | I led the same approach at a workplace-communications hardware company: profiling 56 source tables and reporting failure rates per 1,000 units across about 680k devices. Here it runs on public data, with no employer data. |
| 0:45–1:10 | README architecture and `docs/data_profile.md` | 30.6 million rows load in 23 seconds with DuckDB. The source profile came before any modelling. |
| 1:10–1:35 | The AFR models and the conformed model key | 476 drives report a model name without its prefix, which would split one model in two. Silver fixes it, keeps the raw value, and a test guards it. |
| 1:35–2:00 | `results/survival.md` and the bathtub curve | Kaplan-Meier is corrected for drives already in service, and the README says where single-quarter curves are noisy. |
| 2:00–2:30 | Numbers: fleet AFR and the forecast | Fleet AFR is 1.24%, with 35 models meeting Backblaze's reporting threshold. The forecast expects 914 failures next quarter, against 1,027 observed this one. |
| 2:30–2:45 | `docs/design_doc.md`, the options table | The decision I'd defend in an interview: Governance in the models themselves: owners and classifications as dbt meta, plus enforced contracts on the reports people use. |
| 2:45–3:00 | Back to the README top | For an operations team, that means spares planned from expected failures, not guesses, from numbers that reconcile. The repo, numbers and design doc are linked under the video. |

## Recording checklist
- Close email, chat and notifications. Zoom the browser to 125% so code is readable.
- Run `make fixture-all` once before recording, so CI-style output is fresh if you show it.
- Keep to one take per section; Loom lets you trim. Aim for 2:45 to 3:10.
- Show real numbers on screen as you say them; never estimate on camera.
- Say "synthetic" out loud wherever the README labels data as synthetic.

## After recording
1. Copy the Loom share link.
2. In `README.md`, replace the roadmap line with `- [x] [3-minute Loom walkthrough](<your Loom link>)` and add the link under the title.
3. Add the link to this project's card on saigwe.github.io.
