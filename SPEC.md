# LogScope Specification

## 1. Purpose

LogScope is a small command-line tool for incident responders who need a quick summary of an application log without opening a dashboard.

The tool must process logs as a stream so that large files, including files of at least 100 MB, are not loaded fully into memory.

## 2. Supported Runtime

Implement LogScope in:
- Python

Choose one runtime before implementation begins and document the choice in the README.

## 3. Expected Log Format

Use one documented line format for generated fixtures and test logs. The recommended format is:

```text
2026-10-01 09:00:00 INFO Application started
2026-10-01 09:03:12 WARN Request took longer than expected
2026-10-01 09:05:44 ERROR Database connection failed
```

Each valid line contains:

1. A timestamp in `YYYY-MM-DD HH:mm:ss` format
2. A level: `INFO`, `WARN`, or `ERROR`
3. A free-text message

A malformed line is any line that cannot be parsed into these fields or contains an invalid timestamp or unsupported level.

Malformed lines must be counted and skipped. They must never terminate processing.

## 4. Command-Line Interface

The executable name is `logscope`.

### 4.1 Summary

```bash
logscope summary app.log
```

The command reports:

- Count of `INFO` lines
- Count of `WARN` lines
- Count of `ERROR` lines
- Top five error messages, ordered by frequency
- First valid timestamp
- Last valid timestamp
- Malformed-line count

If error-message counts are tied, use a documented deterministic tie-breaker, such as alphabetical order.

### 4.2 Timeline

```bash
logscope timeline app.log --bucket 15m
```

The command:

- Counts `ERROR` entries in each time bucket
- Displays the result as a text bar chart in the default terminal output
- Reports the malformed-line count

The first required bucket size is `15m`. The implementation may support additional bucket sizes, but this is not required for acceptance.

Time buckets must be aligned consistently to clock boundaries. For example, a `15m` bucket uses `09:00`, `09:15`, `09:30`, and `09:45` boundaries.

### 4.3 Grep

```bash
logscope grep app.log --level ERROR --since "2026-10-01 09:00"
```

The command:

- Prints valid lines matching the selected level
- Includes only entries at or after the `--since` timestamp
- Reports the malformed-line count without treating malformed lines as matches

`--level` accepts `INFO`, `WARN`, or `ERROR`.

## 5. Output Formats

Every command supports:

```bash
--format text
--format json
--format md
```

- `text` is the default and writes human-readable output to standard output.
- `json` writes valid machine-readable JSON to standard output.
- `md` writes a Markdown report file rather than printing the full report to standard output.

For Markdown output, use a predictable filename derived from the input file and command, unless an explicit output option is added and documented. After writing the report, print its path.

All formats must contain the command's main result and malformed-line count. JSON output must use stable field names suitable for automated testing.

## 6. Error Handling

LogScope must:

- Return a non-zero exit code for an unreadable or missing input file
- Return a non-zero exit code for invalid CLI arguments
- Return a non-zero exit code for an invalid timestamp or bucket value
- Print concise, actionable errors to standard error
- Continue processing when individual log lines are malformed
- Avoid unhandled stack traces during normal user errors

## 7. Performance and Memory

- Read the input incrementally, line by line or as a stream.
- Do not read the entire file into memory.
- Process a generated 100 MB log in under 60 seconds in the documented test environment.
- Memory usage must remain stable as file size increases. Small bounded data structures, such as level counters, time buckets, and error-message frequency maps, are acceptable.

The benchmark result must record:

- Runtime and runtime version
- Operating system or environment
- Input file size
- Command executed
- Elapsed time
- Peak memory measurement

## 8. Testing

Provide unit tests for:

- Valid log-line parsing
- Malformed lines
- Invalid timestamps and levels
- `summary`
- Top-five error ordering
- `timeline` bucket boundaries and bar-chart data
- `grep` level and time filtering
- Text, JSON, and Markdown output
- Empty files and files containing only malformed lines

All three commands must also be tested against `sample.log`.

Log fixtures, `sample.log`, and large synthetic logs are intentionally created during later implementation steps, not in the initial specification commit.

## 9. Synthetic Log Generator

Add `scripts/gen_log` later in the project, after the commands and output formats are implemented.

The generator must:

- Create a reproducible synthetic log when given a fixed seed
- Generate valid `INFO`, `WARN`, and `ERROR` lines
- Include a configurable proportion of malformed lines
- Support creation of an approximately 100 MB file
- Avoid holding the full generated log in memory

Generated large log files must not be committed to Git.

## 10. Delivery and Acceptance Criteria

The work is accepted when:

- `summary`, `timeline`, and `grep` work on `sample.log`
- Parser and command unit tests pass
- Text, JSON, and Markdown formats work for every command
- Malformed lines are counted, reported, skipped, and never crash the tool
- A 100 MB generated log is processed in under 60 seconds
- Memory remains stable during the 100 MB test
- Benchmark results and environment details are documented
- Git history shows a reviewed plan followed by small implementation commits
- Generated large logs and reports are excluded from Git where appropriate


