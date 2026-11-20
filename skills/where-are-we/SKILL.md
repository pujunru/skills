---
name: where-are-we
description: Use whenever the user is confused mid-task about where things stand or what you are asking — "where are we", "recap", "I'm lost", "what do you want from me", "what do you actually need", "explain your question", "why are you asking this", "wait, what?". Replies with a strict five-part status report (past context, current progress, blockers, the one action needed from the user with its intent and expected result, forecast) and then stops.
user-invocable: true
---

# Where Are We

The user is in the middle of a task and has lost the thread. Too many decisions
piled up, or you asked a question whose intent is unclear. Your job is to make
the situation readable in one screen, then stop.

## Rules

1. **Stop the work.** Do not edit files, run state-changing commands, or start
   the next step. Read-only checks (`git status`, reading a log, listing a
   resource) are allowed only to confirm a fact you are about to state.
2. **Use the template below exactly.** Same five headings, same order, same
   field labels. Never skip a section, never add one. If a section has nothing,
   write `None.`
3. **Facts, not narration.** Each bullet states a result, not the story of how
   you got there. Mark anything you have not verified with `(unverified)`.
4. **Plain words.** No unexplained jargon, IDs, or internal names. If you must
   name a file, branch, or command, say what it is in the same line.
5. **One ask.** Section 4 holds at most one action. If several things are
   pending, pick the one that unblocks the most and list the rest under
   a `Later:` bullet at the end of Section 5.
6. **Re-state your earlier question honestly.** If you asked the user something
   before, Section 4 replaces it. Say what you actually need, not the proxy
   question you asked. If the old question was the wrong question, say so.
7. **Budget:** at most 250 words in total. Each bullet at most 25 words.
8. **End after Section 5.** No closing paragraph, no extra offer. Wait for the
   user.

## Template

```markdown
## Where are we

### 1. Past context
- **Goal:** <the user's original ask, in one line, in their words>
- **Done:** <finished result> (up to 5 bullets, oldest first)
- **Decided:** <decision> — <who decided: you / me>

### 2. Current progress
- **Now:** <the one step in progress, one sentence>
- **Status:** <how far along: e.g. "3 of 5 steps done", what works, what is not verified>

### 3. Blockers
- **<blocker>:** <cause> → <what would clear it>

### 4. What I need from you
- **Action:** <one imperative sentence: exactly what the user should do or answer>
- **Intent:** <why: which decision or step this unlocks>
- **Expected result:** <the concrete thing you need back: a choice, a value, a file, an approval>
- **Options:** <A — consequence (recommended) / B — consequence; omit this line if not a choice>

### 5. Forecast
- **If you do it:** <the next 1–3 steps and the end state>
- **If not:** <what happens instead: I wait / I take default X / the task stops at Y>
- **Risk:** <the most likely thing to go wrong next, or None.>
- **Later:** <other pending asks, with the default you will use; omit if none>
```

When nothing is needed from the user, Section 4 is exactly:

```markdown
### 4. What I need from you
- **Action:** None — I can continue on my own.
- **Intent:** None.
- **Expected result:** None.
```

## Before you send

Check each item. Fix the report if any check fails.

- Five `###` headings, numbered 1–5, in the order above.
- Section 4 has exactly one `Action:` line, and it is a sentence the user can
  act on without reading anything else.
- `Expected result:` names something concrete, never "your thoughts" or
  "feedback".
- No section is empty; empty ones say `None.`
- Total is 250 words or fewer.
