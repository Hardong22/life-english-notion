# How it works and how to maintain it

[中文](DESIGN.md) | English · [User guide](../README.en.md)

## Conversation and records

The Skill tracks the activity, feedback pace, recording state, and explanation language separately. You can play a restaurant customer, ask for corrections after each sentence, and pause recording at the same time. Changing one setting does not automatically change the others.

Feedback waits until the learner finishes by default. Repeating a model answer and answering independently provide different evidence. Review status changes only after a real response. Attempts at the same expression keep their history; the latest relevant evidence determines the current status. Repeated records do not count as additional learned expressions.

Notion stores the records. Before saving, the Skill confirms the destination, assigns a stable session ID, and checks for duplicates. It reads the result back afterward. If the outcome is unclear, it checks existing pages before attempting another write. `SKILL.md` and `references/` hold the operating rules, so translated documentation does not create a second set of instructions to maintain.

## Files

| Location | Contents |
|---|---|
| `SKILL.md` | Entry point, controls, and shared rules |
| `agents/openai.yaml` | Client display information |
| `references/` | Conversation, review, and Notion workflows |
| `preferences.example.md` | Settings template without personal data |
| `README.md`, `README.en.md` | Chinese and English user guides |
| `docs/` | Chinese and English maintenance notes and practice scenarios |
| `scripts/check_project.py` | Release manifest, links, and common privacy checks |
| `tests/` | Checker tests using synthetic data |
| `.github/workflows/check.yml` | Runs the same checks in GitHub Actions on every push |

## Before publishing

Run these from the repository root with Python 3.10+. No extra dependencies are required.

```bash
python3 scripts/check_project.py
python3 -m unittest discover -s tests -v
python3 scripts/check_project.py --history
```

The checker uses an explicit release manifest and looks for tracked Git files outside it. It checks common privacy patterns in file contents and the `SKILL.md` metadata. `--history` also checks commit identities and historical files reachable from local branches and tags. The default check reads new, uncommitted manifest files from the working directory as well. GitHub Actions runs the same three commands on every push.

Use a GitHub `noreply` address for commits. The checker also accepts other `noreply@…` bot addresses, such as GitHub web merges or AI tool co-author trailers. Keep `preferences.local.md`, `private-records/`, transcripts, and credentials out of the release manifest. `.gitignore` does not protect files that Git already tracks. If sensitive information is found, check earlier commits as well as current files.

Automated detection covers only some risks. Read the actual diff before publishing. A clean history check does not prove that remote caches, other references, or copies held by others have been removed.

## What testing establishes

Checker tests validate packaging rules, not teaching results. Use the [practice scenarios](BEHAVIOR.en.md) to check conversation behaviour, especially language changes, paused recording, leaving a role, and uncertain saves. Do not describe voice or Notion integration as verified until they have been tested in practice.
