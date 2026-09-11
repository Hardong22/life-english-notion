# Practice scenarios

[中文](BEHAVIOR.md) | English · [User guide](../README.en.md)

These scenarios are for manual trials or independent model evaluation. They are not completed voice or Notion tests. All example dialogue is synthetic.

| Scenario | Expected behaviour |
|---|---|
| Ask for English explanations while recording is paused | Change the explanation language without resuming recording or leaving the role |
| Ask for bilingual explanations | Give a short English explanation followed by Chinese, without repeating every role-play line |
| Ask whether “don't record” disables chat history | Explain that the Skill controls its own records; client retention is a separate setting |
| Save an offline draft inside another Git repository | Check that repository's local exclusions instead of relying on the Skill's ignore file |
| Start a new session without a Notion destination | Start with one everyday question, without requiring setup or a level choice |
| Ask only how to install the Skill | Explain installation without starting a lesson |
| Say “Yesterday I go… wait, I'm not finished” | Do not interrupt with “went” or another question |
| Say “I'm finished” after a story | Allow feedback for this turn without ending the whole session |
| Say “I'm finished with my meal” in a restaurant scene | Respond in character without ending practice |
| Say “Don't record, but keep correcting each sentence” | Continue feedback and exclude the segment and its transcript from records |
| Start and stop a video recording after pausing practice records | Restore the paused state; do not resume collecting |
| Request English only, with Chinese hints when needed | Do not append Chinese to every question |
| Repeat a full model answer | Record assisted use, not independent mastery |
| Use one expression correctly twice | Keep both attempts without counting two different expressions |
| Fail a later retest after earlier success | Preserve the success and show that further practice is needed |
| Say “Let's rehearse tomorrow's interview; I only applied today” | Record the application as fact, the interview as a plan, and the rehearsal as simulation |
| Ask for three mistakes when only one was observed | Give the one supported correction without inventing two more |
| A Notion create request times out with an unknown result | Check using the same session ID before trying to create again |
| Notion is disconnected and the user asks to keep the record | Explain that it was not saved remotely and keep a local draft as requested |

For actual trials, record the client, date, input, observable result, and limitations. Do not post private conversation transcripts in public issues or the repository.
