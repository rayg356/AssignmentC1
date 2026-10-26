# LogScope Implementation Plan

## Repository state
- `README.md`, `SPEC.md`, and `INSTRUCTION.md` are present.
- `SPEC.md` is the source of truth for behavior and acceptance.
- Implementation starts after this plan is reviewed and committed.

## Runtime and dependencies
- Runtime: **Python 3.11+**
- Application dependencies: **none** (Python standard library only)
- Test dependency: **pytest**

Rationale:
- Python is required by the specification.
- Standard library supports deterministic streaming parsing, CLI handling, JSON, and file I/O.
- `pytest` keeps tests concise and readable.

## Stage 1 — Parser

### Goal
Create a deterministic streaming parser reusable by all commands.

### Files to add/change
- Create: `logscope/parser.py`
- Create: `tests/test_parser.py`
- Update: `README.md` (runtime + log format contract)

### Tests to add
- Parse valid line into timestamp, level, message.
- Reject malformed structure.
- Reject invalid timestamps.
- Reject unsupported levels.
- Handle empty/whitespace lines as malformed.

### Key design decisions
- Fixed line contract: `YYYY-MM-DD HH:mm:ss LEVEL message`.
- Strict timestamp parse via `datetime.strptime`.
- Parser returns either a valid record or malformed indicator (no fatal exception for bad input).
- Keep per-line parsing isolated and pure for reuse and testability.

### Proposed commit message
`feat: add streaming log parser`

## Stage 2 — Summary command

### Goal
Implement `logscope summary <file>` with counts, top errors, first/last timestamp, malformed count.

### Files to add/change
- Create: `logscope/commands/summary.py`
- Create/Update: `logscope/cli.py`
- Create/Update: `logscope/main.py`
- Create: `tests/test_summary.py`

### Tests to add
- INFO/WARN/ERROR counts.
- Top five ERROR messages.
- Deterministic tie-break ordering.
- First and last valid timestamp.
- Malformed lines counted and skipped.
- Empty file and malformed-only file behavior.

### Key design decisions
- Single pass over file stream.
- Use bounded structures: counters + timestamp min/max.
- Top errors sorted by frequency desc, message asc for deterministic output.

### Proposed commit message
`feat: add summary command`

## Stage 3 — Timeline command

### Goal
Implement `logscope timeline <file> --bucket 15m` with aligned buckets and text bar chart.

### Files to add/change
- Create: `logscope/commands/timeline.py`
- Create: `tests/test_timeline.py`
- Update: CLI wiring in `logscope/cli.py` / `logscope/main.py`

### Tests to add
- 15-minute boundary alignment.
- ERROR-only counting.
- Deterministic bucket ordering.
- Malformed count reporting.
- Empty and malformed-only input behavior.

### Key design decisions
- Bucket floor aligned to clock boundaries (`:00`, `:15`, `:30`, `:45`).
- Deterministic chart scaling.
- Stream file once; aggregate per bucket.

### Proposed commit message
`feat: add timeline command`

## Stage 4 — Grep command

### Goal
Implement `logscope grep <file> --level <LEVEL> --since "YYYY-MM-DD HH:MM"` filtering.

### Files to add/change
- Create: `logscope/commands/grep_cmd.py`
- Create: `tests/test_grep.py`
- Update: CLI wiring in `logscope/cli.py` / `logscope/main.py`

### Tests to add
- Filter by level.
- Filter by since timestamp (inclusive).
- Invalid `--since` returns non-zero with concise stderr.
- Malformed lines are counted, never matched.

### Key design decisions
- Strict `--since` parsing with `%Y-%m-%d %H:%M`.
- Compare only valid parsed records.
- Stream output without loading full input.

### Proposed commit message
`feat: add grep command`

## Stage 5 — Output formats

### Goal
Support `--format text|json|md` for all commands.

### Files to add/change
- Create: `logscope/renderers.py`
- Update: command modules to return structured payloads
- Update: `logscope/cli.py` / `logscope/main.py` format handling
- Create: `tests/test_formats.py`
- Update: `.gitignore` (generated reports)

### Tests to add
- Text output deterministic and complete.
- JSON output valid and stable field names.
- Markdown writes predictable report file and prints path.
- Every command includes malformed-line count in all formats.

### Key design decisions
- Separate computation from rendering.
- Stable JSON schema for automation.
- Predictable markdown filename from input + command.

### Proposed commit message
`feat: add JSON and Markdown output formats`

## Stage 6 — Synthetic-log generator and benchmark

### Goal
Add streaming log generator and benchmark ~100 MB processing.

### Files to add/change
- Create: `scripts/gen_log.py`
- Create: `tests/test_gen_log.py`
- Create: `BENCHMARK.md`
- Update: `README.md` (generator and benchmark usage)
- Update: `.gitignore` (large generated logs/reports)

### Tests to add
- Deterministic output for fixed seed.
- Approximate malformed frequency.
- Size-target behavior.
- No dependence on 100 MB file for normal test suite.

### Key design decisions
- Line-by-line generation until target size reached.
- Seeded RNG for reproducibility.
- Benchmark records runtime version, OS/environment, command, input size, elapsed time, peak memory.

### Proposed commit messages
- `test: add synthetic log generator and performance benchmark`
- `docs: record benchmark results and usage`

## Ambiguities, assumptions, and risks

### Ambiguities
- Whether timeline should include zero-count buckets across the full min→max range.
- Exact markdown output location when no explicit output option exists.

### Assumptions
- Timeline includes continuous aligned buckets from first to last valid timestamp.
- Markdown report is written next to input log with predictable filename.

### Performance risks
- Many unique error messages may increase counter size.
- Very wide time ranges may create many timeline buckets.

### Mitigations
- Keep streaming processing for input reading.
- Restrict in-memory state to required aggregates only.
- Deterministic rendering and ordering to keep tests stable.

## Acceptance checks
- [ ] `summary`, `timeline`, and `grep` work on `sample.log`.
- [ ] Parser and command tests pass.
- [ ] Text, JSON, and Markdown formats work for every command.
- [ ] Malformed lines are counted, reported, skipped, and never crash processing.
- [ ] Generated ~100 MB log processes in under 60 seconds in documented environment.
- [ ] Memory remains stable as input grows.
- [ ] Benchmark commands, environment details, and measurements are documented.
- [ ] Git history shows reviewed plan then staged implementation commits.
- [ ] Generated large logs and report artifacts are excluded from Git.

## Planned commit sequence
1. `docs: add reviewed implementation plan`
2. `feat: add streaming log parser`
3. `feat: add summary command`
4. `feat: add timeline command`
5. `feat: add grep command`
6. `feat: add JSON and Markdown output formats`
7. `test: add synthetic log generator and performance benchmark`
8. `docs: record benchmark results and usage`
