# Stage 6 Benchmark

## Environment

- Runtime: Python 3.12.10
- Platform: Windows-11-10.0.26200-SP0
- Working directory: `C:/Users/ray.goh/Downloads/AssignmentC1-main/AssignmentC1-main`
- Input file: `generated/synthetic-100mb.log`
- Exact input size: `104857623` bytes

## Commands measured

1. `python -m logscope.main summary generated/synthetic-100mb.log --format text`
2. `python -m logscope.main timeline generated/synthetic-100mb.log --bucket 15m --format text`
3. `python -m logscope.main grep generated/synthetic-100mb.log --level ERROR --since "2026-10-01 09:00" --format text`

## Results

| Command | Elapsed runtime (seconds) | Peak memory (bytes) | Exit code |
|---|---:|---:|---:|
| summary | 12.018648 | 44180 | 0 |
| timeline | 15.033965 | 1086237 | 0 |
| grep | 14.773238 | 39318159 | 0 |

## Notes

- Timings and memory values are measured from a local run.
- Peak memory above is Python allocator peak (`tracemalloc`) for the benchmark runner process while invoking each command.
- Raw command outputs were captured into:
  - `generated/summary.bench.txt`
  - `generated/timeline.bench.txt`
  - `generated/grep.bench.txt`
