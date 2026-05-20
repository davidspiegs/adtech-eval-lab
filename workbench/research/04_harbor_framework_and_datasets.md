## Harbor Framework & Dataset Hub Research

> Note: WebSearch and WebFetch were not available during this research session. The findings
> below are derived entirely from the sample task at
> `restaurant-weekly-cost-control-audit/` and four completed job runs stored alongside it.
> If online docs become available, supplement this with material from
> `harborframework.com/docs/getting-started` and `hub.harborframework.com/datasets`.

---

### Framework Overview & Key Concepts

Harbor is a benchmark framework for evaluating AI coding agents on realistic,
containerized tasks. Key concepts observed from the sample project:

| Concept | Description |
|---------|-------------|
| **Task** | A self-contained directory with `task.toml`, `instruction.md`, `environment/`, `tests/`, and `solution/`. |
| **Environment** | A Docker container built from `environment/Dockerfile` that provides the agent's workspace (files, tools, libraries). |
| **Agent** | The AI system under test (e.g. `claude-code` with `claude-sonnet-4-5`). An `oracle` agent exists for validation -- it runs the gold solution to confirm the tests pass. |
| **Verifier** | A script (`tests/test.sh`) that runs after the agent finishes, executes pytest, and writes a binary reward (`0` or `1`) to `/logs/verifier/reward.txt`. |
| **Trial** | A single agent-on-task execution. Multiple trials can run per job. |
| **Job** | A batch of one or more trials. Configured via `config.json` with settings for concurrency, timeouts, agent selection, and retry policy. |
| **ATIF Trajectory** | The full trace of the agent's session, stored as `trajectory.json` using schema `ATIF-v1.2`. |
| **Skills** | Markdown documents and helper scripts placed in `environment/skills/` and copied into the container for multiple agent formats (Claude Code, Codex, Goose, Gemini, etc.). |
| **CTRF** | Common Test Report Format -- pytest results are exported to `ctrf.json` to give structured per-test pass/fail data alongside the binary reward. |

**Lifecycle of a run (observed from timestamps in `result.json`):**

1. **Environment setup** -- Docker image build (~40 s in sample).
2. **Agent setup** -- Agent initialization inside the container (~2 min).
3. **Agent execution** -- The agent reads the instruction and works (~2.5 min).
4. **Verifier** -- `test.sh` runs pytest and writes reward (~14 s).

---

### Task Structure & File Format (from sample)

A Harbor task directory follows this exact layout:

```
restaurant-weekly-cost-control-audit/
  task.toml                     # metadata + resource limits
  instruction.md                # the prompt the agent receives
  environment/
    Dockerfile                  # container image definition
    data/                       # input data files + build script
      build_inputs.py           # runs at image build time to prepare data
      pos_sales.csv
      recipes.json
      inventory_open.csv
      inventory_close.csv
      historical.csv
      invoices/
        vendor_sysco.pdf
        vendor_local.pdf
        vendor_beverage.pdf
    skills/                     # agent skill files (copied to many paths)
      business-kpi-formulas/
        SKILL.md
        references/formulas.md
      csv-tools/SKILL.md
      pdf/
        SKILL.md
        scripts/extract_invoice_rows.py
      xlsx/
        SKILL.md
        scripts/write_table.py
      fuzzy-match/SKILL.md
      ...
  tests/
    test.sh                     # verifier entry point
    test_outputs.py             # pytest assertions
  solution/
    solve.sh                    # gold-standard solution (used by oracle agent)
  jobs/                         # run artifacts (not part of the task spec itself)
```

#### task.toml

```toml
version = "1.0"

[metadata]
author_name = "Adtech Eval Lab"
author_email = ""
difficulty = "hard"
category = "restaurant-operations"
tags = ["finance", "cogs", "labor", "pdf", "xlsx", "inventory", "audit"]

[verifier]
timeout_sec = 900.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 4096
storage_mb = 10240

[environment.env]
GEMINI_CLI_TRUST_WORKSPACE = "true"
```

Key fields:
- `version` -- always `"1.0"` in the sample.
- `[metadata]` -- descriptive fields: `difficulty` (easy/medium/hard), `category`, `tags`.
- `[verifier]` and `[agent]` -- `timeout_sec` caps how long each phase runs.
- `[environment]` -- Docker resource limits (`cpus`, `memory_mb`, `storage_mb`, `build_timeout_sec`).
- `[environment.env]` -- environment variables injected into the container.

#### instruction.md

The instruction is a plain-English prompt written as if a human stakeholder is speaking
to the agent. Key conventions observed:

- Specifies the **output path** explicitly (`/root/audit_report.xlsx`).
- Lists **all input files** and their locations.
- Prescribes **exact sheet names** and **exact column header strings**.
- Defines **business rules** (thresholds, flag labels, weekend definitions).
- States that numeric values must be stored as numbers, not text.
- Written to be self-contained: an agent with no prior context can complete the task
  from this document alone.

#### Dockerfile

- Base: `ubuntu:24.04`
- Installs Python 3 + pip + domain libraries (`openpyxl`, `pandas`, `pdfplumber`, `rapidfuzz`).
- Copies raw data to `/tmp/task-data`, then runs `build_inputs.py` to stage files in `/root/data`.
- Copies `skills/` into multiple agent-specific paths:
  - `/root/.claude/skills` (Claude Code)
  - `/root/.codex/skills` (Codex)
  - `/root/.opencode/skill` (OpenCode)
  - `/root/.goose/skills` (Goose)
  - `/root/.factory/skills` (Factory)
  - `/root/.agents/skills` (Portable agents)
  - `/root/.github/skills` (GitHub Copilot)
  - `/root/.gemini/skills` (Gemini)

**Design note:** The `build_inputs.py` script generates some inputs at build time
(e.g. the labor schedule XLSX is synthesized from inline data). This lets the task
author control exact values while keeping the Dockerfile clean.

---

### Verifier Design Patterns

The verification pipeline is a two-stage process:

**Stage 1: `test.sh` (entry point)**

```bash
#!/bin/bash
pip3 install --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 openpyxl==3.1.5
mkdir -p /logs/verifier
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v
PYTEST_EXIT_CODE=$?
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

Key patterns:
- Installs test dependencies at verification time (not baked into the image).
- Uses `pytest-json-ctrf` to produce machine-readable test results.
- Writes `/logs/verifier/ctrf.json` (per-test details) and `/logs/verifier/reward.txt` (binary 0/1).
- **Always exits 0** -- the reward file is the signal, not the script exit code.
- Reward is all-or-nothing: 1 only if every test passes, 0 otherwise.

**Stage 2: `test_outputs.py` (assertions)**

The test file validates the agent's output artifact (`/root/audit_report.xlsx`).
Design patterns observed:

1. **File existence check** -- Fail fast if the output file is missing.
2. **Sheet presence check** -- Verify all required sheet names exist.
3. **Column header parsing** -- Use a `header_map()` helper to locate columns by name, making tests resilient to extra columns.
4. **Exact value assertions** -- Check specific computed values (e.g. `food_cogs == 2147.5`) with tight tolerances (`abs(x - expected) < 0.01`).
5. **Flag logic validation** -- Verify that flagged/unflagged items match expected sets.
6. **Multi-section navigation** -- For sheets with stacked tables (separated by blank rows), the test searches for section headers to find the right rows.
7. **Cross-sheet consistency** -- The final test reads from both "Prime Cost Summary" and "Executive Summary" to validate derived values.

**Observed failure modes from the 4 job runs:**

| Run | Agent | Reward | Tests Passed | Failure |
|-----|-------|--------|-------------|---------|
| 11-48-13 | oracle | 1.0 | 5/5 | -- (gold solution passes) |
| 12-03-50 | claude-code (sonnet 4.5) | 0.0 | 4/5 | WoW change: got 0.04413, expected 0.0453 |
| 12-32-44 | claude-code (sonnet 4.5) | 0.0 | 3/5 | Date format mismatch + WoW change wrong |
| 12-41-09 | claude-code (sonnet 4.5) | 0.0 | 3/5 | Same two failures as above |

Common agent mistakes:
- **Numeric precision errors** in derived calculations (week-over-week change off by ~0.001).
- **Date format mismatches** -- dates stored as datetime objects instead of `YYYY-MM-DD` strings, causing lookup failures.

---

### Environment Configuration Best Practices

From the sample task, several environment design principles emerge:

1. **Use `build_inputs.py` for data staging** -- Generate or transform data at build time. This keeps raw source data clean and lets you synthesize controlled inputs (like the XLSX labor schedule) with exact values.

2. **Pin all library versions** -- Both in the Dockerfile (`openpyxl==3.1.5`, `pandas==2.2.3`) and in `test.sh` (`pytest==8.4.1`). This ensures reproducibility.

3. **Set generous but bounded resource limits** -- The sample uses 1 CPU, 4 GB RAM, 10 GB storage. These are enough for data processing but prevent runaway consumption.

4. **Provide skills for multiple agent formats** -- Copy skill files to 8+ agent-specific paths so any supported agent can discover them.

5. **Skills as guardrails** -- The skills provide formula definitions (`business-kpi-formulas`), tool-specific patterns (`pdf`, `xlsx`), and validation checklists (`csv-tools`). They guide the agent toward deterministic, correct behavior without giving away the full solution.

6. **Keep the working directory at `/root`** -- Both input data (`/root/data/`) and expected output (`/root/audit_report.xlsx`) live under `/root`.

7. **Separate verifier dependencies from agent dependencies** -- The Dockerfile installs what the agent needs; `test.sh` installs what the verifier needs. This prevents the agent from depending on test libraries.

---

### ATIF Trajectory Format

The Agent Trajectory Interchange Format (ATIF) version 1.2 records the full session. Structure:

```json
{
  "schema_version": "ATIF-v1.2",
  "session_id": "uuid",
  "agent": {
    "name": "claude-code",
    "version": "2.1.92",
    "model_name": "claude-sonnet-4-5-20250929",
    "extra": {
      "cwds": ["/root"],
      "git_branches": ["HEAD"]
    }
  },
  "steps": [
    {
      "step_id": 1,
      "timestamp": "ISO-8601",
      "source": "user",         // or "agent"
      "message": "...",
      "extra": { "is_sidechain": false }
    },
    {
      "step_id": 2,
      "source": "agent",
      "model_name": "...",
      "message": "",
      "reasoning_content": "...",  // extended thinking (present on agent steps)
      "metrics": {
        "prompt_tokens": 16987,
        "completion_tokens": 737,
        "cached_tokens": 0,
        "extra": {
          "cache_creation_input_tokens": 16978,
          "cache_read_input_tokens": 0,
          "server_tool_use": { "web_search_requests": 0, "web_fetch_requests": 0 },
          "service_tier": "standard"
        }
      }
    },
    {
      "step_id": 4,
      "source": "agent",
      "message": "Executed Bash ...",
      "tool_calls": [
        {
          "tool_call_id": "toolu_...",
          "function_name": "Bash",
          "arguments": { "command": "ls -la /root/data/", "description": "..." }
        }
      ],
      "observation": {
        "results": [
          {
            "source_call_id": "toolu_...",
            "content": "stdout output..."
          }
        ]
      }
    }
  ]
}
```

Key fields per step:
- `source` -- `"user"` for the initial instruction, `"agent"` for model actions.
- `reasoning_content` -- The agent's chain-of-thought (extended thinking).
- `tool_calls` -- Array of tool invocations with function name and arguments.
- `observation.results` -- Tool outputs, including stdout/stderr from Bash calls.
- `metrics` -- Token counts and caching statistics per agent step.
- `extra` -- Metadata including `cwd`, `is_sidechain`, tool result details.

---

### Best Practices for Task Design

Based on analysis of the sample task and its 4 job runs:

**1. Write the solution first, then derive tests from it.**
The oracle agent (which runs `solution/solve.sh`) achieved reward 1.0, confirming the
solution and tests are consistent. Always validate this round-trip before publishing a task.

**2. Make the instruction self-contained.**
The agent receives only `instruction.md`. Every piece of information needed -- file paths,
column names, business rules, thresholds, output format -- must be in that document.

**3. Specify exact string literals for anything the verifier checks.**
Sheet names, column headers, flag values ("ALERT", "investigate"), action labels
("On Track", "Monitor", "Immediate Action"), and date formats ("YYYY-MM-DD") must be
stated verbatim in the instruction. The sample task does this well.

**4. Use tight but fair numerical tolerances.**
The sample uses `abs(x - expected) < 0.01` for dollar values and `< 0.000001` for
percentages. The WoW change tolerance of 0.000001 caught a real agent error (off by
~0.001), but this tight tolerance also means the agent must follow the exact same
calculation path as the solution.

**5. Design for common agent failure modes.**
The job runs reveal two recurring issues:
- **Date formatting** -- Agents may store dates as datetime objects instead of strings. The
  test searches for `"2026-03-23"` as a string, so the instruction should explicitly say
  to store dates as `YYYY-MM-DD` strings.
- **Calculation order sensitivity** -- Different aggregation orders can produce slightly
  different floating-point results. Define the calculation path clearly.

**6. Provide skills that guide without solving.**
The skills give formula definitions and tool patterns but do not contain the full solution.
This helps agents avoid common mistakes (like storing percentages as display text) while
still requiring them to integrate multiple data sources and produce the output.

**7. Use binary reward with all-or-nothing pass criteria.**
The verifier writes `1` only if all tests pass. This means each test should cover an
independent, meaningful aspect of correctness. The sample has 5 tests covering:
sheet existence, COGS values, variance flags, labor analysis, and prime cost/executive
summary.

**8. Structure tests from simple to complex.**
The sample tests are ordered: file exists -> sheet names -> simple table values ->
multi-section navigation -> cross-sheet derived values. This gives useful diagnostic
information even when the binary reward is 0.

**9. Use CTRF for diagnostic detail.**
The `ctrf.json` output shows exactly which tests passed and which failed, with full
tracebacks. This is invaluable for debugging agent behavior even though the reward is
binary.

**10. Test with the oracle agent before running real agents.**
The first job run (11-48-13) used the oracle agent to validate the task. This is a
critical step -- it confirms the solution, tests, environment, and data are all correct.

---

### Checklist for Building New Tasks

- [ ] **Define the output artifact** -- What file does the agent produce? Where?
- [ ] **Create input data** -- Place raw files in `environment/data/`. Use `build_inputs.py` if any inputs need generation or transformation at build time.
- [ ] **Write `instruction.md`** -- Self-contained prompt with all file paths, column names, business rules, and output format. State exact string literals the verifier will check.
- [ ] **Write `solution/solve.sh`** -- Gold-standard solution that produces the correct output. Use a heredoc-embedded Python script or call a script file.
- [ ] **Write `tests/test_outputs.py`** -- Pytest assertions that validate the output. Cover:
  - File existence
  - Structural requirements (sheet names, column headers)
  - Key computed values with appropriate tolerances
  - Flag/label logic
  - Cross-section/cross-sheet consistency
- [ ] **Write `tests/test.sh`** -- Install test deps, run pytest with CTRF output, write reward file. Always `exit 0`.
- [ ] **Write `environment/Dockerfile`** -- Base image, library installs (pinned versions), data staging, skill copying.
- [ ] **Write `task.toml`** -- Set version, metadata, timeouts, resource limits, and any environment variables.
- [ ] **Create skills** -- Write `SKILL.md` files with domain formulas and tool-specific guidance. Include reference scripts if helpful.
- [ ] **Run oracle agent** -- Execute the task with the oracle agent to validate the full pipeline (environment build -> solution -> verifier -> reward = 1).
- [ ] **Run a real agent** -- Execute with at least one AI agent (e.g. `claude-code`) to verify the task is solvable but non-trivial. Check CTRF output for meaningful failure patterns.
- [ ] **Review tolerances** -- Ensure numerical tolerances are tight enough to catch real errors but loose enough to accept valid alternative calculation paths.
- [ ] **Verify date/string conventions** -- If the verifier checks string values (dates, labels), confirm the instruction specifies the exact format.
