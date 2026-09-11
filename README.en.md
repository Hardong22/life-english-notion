# Life English Notion

[中文](README.md) | English

Talk about your day in Codex and practise putting it into English. When you want to rehearse ordering coffee, an interview, or a conversation at work, switch to role-play. At the end, you can save a summary and expressions to review to a Notion page you choose.

This is an installable Skill that you can use in new chats. You do not need to run a separate website. Text practice works in chat; voice requires support from your client. Saving records requires a Notion connection and a destination page.

## Install and start

Send this in Codex:

```text
Use $skill-installer to install https://github.com/Hardong22/life-english-notion
```

The Skill is at the repository root. If the installer asks for a path, use the root and the name `life-english-notion`. See the [OpenAI Skills Catalog](https://github.com/openai/skills) for installation guidance. Keep only one installation with this name.

After installation, open a new chat:

```text
Use $life-english-notion to start today's English practice.
```

Try speaking in English first. If you get stuck, describe what you mean or add a few words in Chinese. By default, feedback waits until you finish and covers one issue at a time. “I'm finished” ends your turn; “Let's wrap up” ends the practice session.

You can also choose a scene right away:

```text
Use $life-english-notion to practise ordering at a coffee shop. Start the role-play without a preview.
```

## Set the pace

| Say | What happens |
|---|---|
| I'm not finished yet | Wait for you to continue, without another question or correction |
| Give me a hint, not the whole sentence | Start with a clue, keyword, or sentence frame |
| Correct me sentence by sentence | Address one issue after each sentence |
| Pause corrections | Continue the topic without feedback |
| Don't record this part | Keep chatting, but exclude this part from practice records and summaries |
| I'm recording a video | Pause interruptions, corrections, and practice recording; restore the previous state afterward |
| Let's wrap up and review | Leave the role, review the session, and save only as agreed |

“Don't record” controls what the Skill collects and saves. It cannot turn off the client's chat history or the service's data retention.

## Switch the explanation language

Say “Explain in Chinese”, “Explain in English”, or “Give bilingual explanations” at any time. This changes usage guidance, correction explanations, and review commentary. Practice dialogue stays mainly in English. To change the dialogue language, say so directly, for example “English only from now on” or “Let's chat in Chinese for a while”.

Changing language does not resume paused recording or leave the current role. A new chat restores only preferences that were actually saved and read.

## Save to Notion

You can practise without Notion and read the summary in chat.

Before the first save, connect Notion and send the Skill your destination page link. To save automatically in future sessions, say:

```text
Save future practice sessions to this page when we finish. Save the destination and this preference locally so new chats can use them.
```

The Skill checks the page and uses its existing structure. If there is no structure yet, it starts with session pages under the chosen parent. Real events, plans, and role-play lines stay separate. Reading a model answer, repeating it, and using an expression independently are recorded differently too.

Local preferences go in `preferences.local.md`; see the [settings template](preferences.example.md). Keep credentials and conversation history out of this file. Installing the Skill does not carry chat history into new sessions. Reviewing past practice requires reading the selected Notion pages.

If Notion is unavailable, the Skill says the record has not been saved. At your request, it can keep a draft in `private-records/` in the current working directory and check for duplicates before syncing later. If that directory belongs to another Git repository, exclude it there as well.

## Privacy and limits

The public repository contains Skill instructions, documentation, and checking scripts. Local settings, practice records, transcripts, and credentials are not part of the release. See the [maintenance notes](docs/DESIGN.en.md) for publication checks.

The client controls voice turn detection, so the instruction to wait cannot guarantee uninterrupted microphone input. The Skill has no pronunciation scoring engine, and text cannot establish pronunciation quality. Voice practice, Notion writes, and preference recovery across chats still need testing in the environment where you use them.

Project checks can catch some file, link, and privacy problems. They cannot prove that every conversation follows the teaching rules or detect every kind of sensitive information. Use the [practice scenarios](docs/BEHAVIOR.en.md) to check actual behaviour after changing the rules.

## License

This project uses the [MIT License](LICENSE). Keep its copyright and permission notice when distributing the project.
