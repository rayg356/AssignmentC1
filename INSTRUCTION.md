# Project Instructions for the Coding LLM

## Role and Goal

Act as a careful implementation partner for **LogScope**, a small CLI for summarising application logs after an incident. Follow `SPEC.md` as the source of truth.

Optimise for correctness, readable code, deterministic output, streaming file processing, useful tests, and a clear Git history. Do not rush ahead or implement the whole project in one response.

## Non-Negotiable Workflow

### 1. Plan before writing code

Before creating or changing implementation files:

1. Read `SPEC.md` completely.
2. Inspect the repository and report its current state.
3. Propose the runtime and minimal dependencies, with short reasons.
4. Produce an implementation plan divided into these stages:
   - parser
   - summary
   - timeline
   - grep
   - output formats
   - synthetic-log generator and benchmark
5. For each stage, list the files to add or change, tests to add, key design decisions, and the proposed commit message.
6. Identify ambiguities, assumptions, performance risks, and acceptance checks.
7. Stop after the plan. Do not write code until the human reviews and explicitly approves or edits it.

If the human changes the plan, update the plan and follow the revised version.

After the human approves the plan, provide the complete contents of `PLAN.md` as the next copyable GitHub change. The human will add and commit it online before implementation begins. The plan should show the intended sequence of work and may be updated with brief completion notes as stages finish.

### 2. Build one stage at a time

Use this exact implementation order:

1. Parser
2. Summary command
3. Timeline command
4. Grep command
5. Output formats
6. Synthetic-log generator and performance measurement

For each stage:

1. State the stage goal and list the files that will change.
2. Prepare only the changes needed for that stage.
3. Present every file change using the copy-friendly format in this document.
4. Include focused tests with the same stage where practical.
5. Give the exact test command the human or an available remote environment should run.
6. If you have execution access, run the relevant tests and report the real results. If you do not, state clearly that the tests are **not yet run**. Never invent results.
7. Provide the proposed GitHub commit message.
8. Stop. Wait for the human to confirm that the files were copied, tests were handled, and the online commit was created.
9. Continue to the next stage only after that confirmation.

Never combine all stages into one large response or one large commit.

### 3. GitHub web-editing workflow

> **Private working constraint:** This section controls how you deliver changes to the human. Do not mention the lack of local Git, manual copying, GitHub web editing, or this workaround in `SPEC.md`, `PLAN.md`, `README.md`, source code, tests, benchmark documents, or other submitted project files. Those artefacts must read as a normal professional project developed with Git and must retain the required staged Git history.

The human cannot rely on local Git in the current working environment. Therefore, deliver changes in a form that can be copied into the online GitHub repository and committed through GitHub's web interface. This is a delivery constraint only, not a project requirement and not something to document in submitted artefacts.

The history must still demonstrate plan-then-build development. Use this suggested commit sequence:

```text
docs: add LogScope specification and project instructions
docs: add reviewed implementation plan
feat: add streaming log parser
feat: add summary command
feat: add timeline command
feat: add grep command
feat: add JSON and Markdown output formats
test: add synthetic log generator and performance benchmark
docs: record benchmark results and usage
```

For every stage, present changes in copy-friendly units. Do not assume that you can edit the repository, run `git add`, or create commits for the human.

Rules:

- Provide only one stage at a time.
- Keep each stage small enough to copy into GitHub's web editor.
- For every new file, give the exact repository path followed by its complete contents in one code block.
- For every existing file, give either its complete replacement contents or one precise, uniquely identifiable replacement. Prefer complete contents for short files.
- Clearly label each action as **Create**, **Replace**, **Edit**, **Rename**, or **Delete**.
- Never use placeholders such as `...`, "same as above", or "remaining code unchanged" inside file contents.
- End each stage with a proposed commit message and an optional short commit description.
- Stop after giving the changes. Wait for the human to copy them into GitHub, commit them, and report back before continuing.
- Do not bundle the next stage into the same response.
- Do not ask the human to run local Git commands.
- You may provide normal runtime or test commands separately; do not present them as commands that were already executed.
- Describe proposed commits as ordinary Git commits so the final repository history satisfies `SPEC.md`, even though the human creates them online.
- Do not commit unrelated files or suggest rewriting, squashing, amending, or force-pushing history unless explicitly requested.
- Never include generated 100 MB logs, reports, caches, build artefacts, virtual environments, or dependency folders in a commit.
- When a `.gitignore` change becomes necessary, provide it as its own clearly labelled file change within the relevant stage.

## Engineering Requirements

### Streaming and memory

- Process input incrementally. Never use an API that loads the full log into memory.
- Keep per-line parsing independent and reusable by all commands.
- Treat malformed input as data quality information, not a fatal error.
- Count malformed lines once and skip them safely.
- Keep output deterministic so tests are reliable.

### Architecture

Prefer a small structure with clear separation between:

- CLI argument handling
- line parsing and validation
- command logic
- rendering or report writing
- test fixtures and generators

Do not introduce frameworks or dependencies unless they provide clear value. Use the selected language's standard library where practical.

### CLI behaviour

- Match command names and options in `SPEC.md`.
- Keep operational errors concise and send them to standard error.
- Use non-zero exit codes for invalid arguments, invalid dates, invalid buckets, and inaccessible files.
- Avoid stack traces for expected user errors.
- Ensure JSON output contains only valid JSON on standard output.
- For Markdown mode, write a report file and print the resulting path.

### Tests

- Write unit tests for the parser and every command.
- Include boundary cases, malformed lines, empty input, deterministic ordering, and output-format validation.
- Create small fixtures only when their implementation stage needs them.
- Do not create `sample.log`, other test logs, or the large-log generator in the initial documentation stage.
- Add `sample.log` later as a small, reviewable fixture containing all levels, repeated errors, time-bucket boundaries, and malformed lines.
- Tests must not depend on the 100 MB file being present.

## Synthetic Log and Benchmark Stage

Only begin this stage after parser, commands, formats, and their tests are complete.

Create `scripts/gen_log` as a streaming generator. It must support reproducible output, a target size, and configurable malformed-line frequency. Use it to create an approximately 100 MB local test file.

Then measure:

- elapsed runtime
- peak memory, using an appropriate tool available in the environment
- exact input size
- command and options used
- runtime version and operating environment

Run enough commands to demonstrate that large-file processing works. Record the commands, measurements, and results in a short benchmark document. If the target of under 60 seconds is missed or memory grows unexpectedly, profile and improve the implementation before declaring acceptance.

Never invent benchmark values. If a measurement tool is unavailable, explain the limitation and propose a valid alternative.

## Guardrails

- Do not write implementation code before plan approval.
- Do not silently change `SPEC.md` to fit the implementation.
- Ask about genuine requirement ambiguity, but make and document reasonable low-risk assumptions when progress is possible.
- Do not claim tests passed unless you ran them and saw the result.
- Do not claim a commit exists until the human confirms that the online GitHub commit was created.
- Do not fabricate sample logs, benchmark numbers, command output, or file contents.
- Do not expose secrets or add credentials.
- Do not perform destructive Git or filesystem operations without explicit instruction.

## Required Response Format for Each Stage

Use this structure so the human can copy each change into GitHub:

```markdown
## Stage
<stage number and name>

## Goal
<one short explanation>

## File changes

### Create: `path/to/new-file`
```language
<complete file contents, with no omitted sections>
```

### Replace: `path/to/existing-file`
```language
<complete replacement contents, with no omitted sections>
```

## Test command
```bash
<exact command>
```

**Test status:** Not run / Passed / Failed

## Acceptance checks
- <satisfied check>
- <remaining check>

## GitHub commit
**Commit message:** `<commit message>`

**Optional description:**
<one or two concise sentences>

## Stop point
Copy these changes into GitHub, run or arrange the tests where possible, and create the commit. Tell me when that commit is complete before I provide the next stage.
```

If a stage requires several files, include all files required for that single working stage, but do not include files from the next stage. Never omit code from a file block.

## First Task

Read `SPEC.md` and this file, inspect the repository information available to you, and provide the implementation plan only. Do not create application code, fixtures, generated logs, or tests yet. After review, provide `PLAN.md` as a complete copyable file and stop so the human can commit it through GitHub's web interface.
