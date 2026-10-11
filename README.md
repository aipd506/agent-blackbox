# agent-blackbox

The Deterministic Flight Data Recorder for Autonomous Coding Sessions. Captures hypotheses, transient diffs, test verdicts, and decision branches with zero-loss resume tokens.

## The Core Problem

Autonomous AI coding agents (operating in Cursor, Claude Desktop, Antigravity, Copilot, or autonomous CLI loops) suffer from acute context amnesia:
1. Session Truncation and Crashes: When a long-running coding session runs out of context tokens, hits rate limits, or crashes, the entire reasoning trajectory is destroyed.
2. Conversational Bloat: Chat logs contain thousands of tokens of pleasantries, tool descriptions, and irrelevant chatter. Re-reading a raw transcript wastes context window capacity and money.
3. Repetitive Failure Loops: A new agent session has no structured memory of failed experiments, transient diffs that broke tests, or abandoned rabbit holes. As a result, agents routinely re-test the exact same failed hypothesis, repeating costly mistakes.

## The Solution

`agent-blackbox` acts as an unalterable flight data recorder mounted into your workspace:
1. Append-Only Flight Telemetry: Automatically records four structured telemetry events into `.blackbox/flight_data.jsonl`:
   1. `HYPOTHESIS`: The agent's proposed technical approach and confidence score.
   2. `MUTATION`: File paths and diff metrics prior to verification.
   3. `VERIFICATION`: Command exit codes, execution durations, and compressed failure diagnostics.
   4. `DECISION`: Outcome status (`CONFIRMED`, `REVERTED`, `PIVOTED`, `ABANDONED`) and rationale.
2. Zero-Loss Resume Tokens: Synthesizes the entire session history into a dense, high-signal 150-token prompt block. It locks in confirmed decisions and explicitly flags failed paths as `DO NOT REPEAT`.
3. Decision Tree Timeline: Generates clean ASCII and Markdown visualizations of the agent's problem-solving path.
4. Native Model Context Protocol (MCP) Server: Exposes flight recorder tools directly to Claude Desktop, Cursor, Antigravity, and Zed over standard JSON-RPC stdio.

## Installation

```bash
pip install agent-blackbox
```

Written in pure Python with zero external runtime dependencies. Runs on any platform with Python 3.8 or higher.

## Quickstart

### 1. Initialize Flight Storage
Run once in your project root:

```bash
blackbox init
```

This creates the `.blackbox/` directory. Add `.blackbox/` to `.gitignore` or commit it for shared multi-agent state.

### 2. Record Session Telemetry

Record a proposed hypothesis:
```bash
blackbox hypothesis --goal "Fix auth deadlock" --text "Use advisory locks instead of row-level lock" --confidence 0.90
```

Record a code mutation:
```bash
blackbox mutation --files "src/auth.py,src/db.py" --added 14 --deleted 3 --diff "+pg_try_advisory_lock"
```

Record test verification:
```bash
blackbox verify --command "pytest tests/test_auth.py" --exit-code 0 --passed --summary "18 passed in 0.42s"
```

Record an architectural decision:
```bash
blackbox decision --status CONFIRMED --rationale "Advisory locks eliminate Postgres lock escalation cleanly"
```

### 3. View the Decision Timeline
Generate a chronological flight audit:

```bash
blackbox timeline
```

Example timeline output:
```
============================================================
             AGENT-BLACKBOX FLIGHT DATA TIMELINE            
============================================================
[19:40:12] Step 01 | [HYPOTHESIS] (confidence: 0.90)
    Goal: Fix auth deadlock
    Proposal: Use advisory locks instead of row-level lock
------------------------------------------------------------
[19:40:25] Step 02 | [MUTATION] Files: src/auth.py, src/db.py (+14, -3)
    Diff: +pg_try_advisory_lock
------------------------------------------------------------
[19:40:32] Step 03 | [VERIFICATION] PASSED (exit 0): `pytest tests/test_auth.py`
    Result: 18 passed in 0.42s
------------------------------------------------------------
[19:40:40] Step 04 | [DECISION] >>> CONFIRMED <<<
    Rationale: Advisory locks eliminate Postgres lock escalation cleanly
============================================================
```

### 4. Generate Zero-Loss Resume Tokens
When resuming after context compaction or handing off to another agent, generate the prompt block:

```bash
blackbox resume
```

Output:
```markdown
[BLACKBOX RESUME CONTEXT]
Goal: Fix auth deadlock
Steps Recorded: 4 telemetry events
Locked In Decisions:
1. Advisory locks eliminate Postgres lock escalation cleanly
Active Files: src/auth.py, src/db.py
Last Test Status: SUCCESS (18 passed in 0.42s)
[END RESUME CONTEXT]
```

## Model Context Protocol (MCP) Integration

`agent-blackbox` includes a built-in MCP server. Configure it in `claude_desktop_config.json` or your Cursor / Antigravity MCP settings:

```json
{
  "mcpServers": {
    "blackbox": {
      "command": "blackbox",
      "args": ["mcp"]
    }
  }
}
```

Available MCP tools:
1. `blackbox_record_hypothesis`: Logs agent hypotheses and goals.
2. `blackbox_record_mutation`: Logs code diffs before testing.
3. `blackbox_record_verification`: Logs test execution results.
4. `blackbox_record_decision`: Locks in confirmed decisions or flags abandoned paths.
5. `blackbox_get_resume_token`: Injects dense resumption context into prompts.
6. `blackbox_get_timeline`: Retrieves formatted decision tree.

## Contributing and License

`agent-blackbox` is free open-source software licensed under the MIT License. Contributions and PRs are welcomed.

### Sovereign Payout and Sponsorship Coordinates
1. Bitcoin Native SegWit: `bc1qaedjdrkrhjya767yvfz676jeyx5an04kfwzczg`
2. Stacks Protocol: `SP3Q5P9MEREY8KQVBRHH4BBVAB4GTKPDYPT80002V`
