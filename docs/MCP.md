# The MCP server — Oxyde over Model Context Protocol

`oxyde-mcp` lets an AI assistant talk to the engine's own tools. It is a
[Model Context Protocol](https://modelcontextprotocol.io) server: point an MCP
client — an editor assistant, a chat client, an agent — at it, and the assistant
can ask Oxyde questions about *your* content and get answers from the engine
itself, not from a guess.

It is the fifth face of **Rusty Gear**, alongside the FUSE language server, the
exact transpiler and compiler, retrieval (`oxtool ask`), and the optional local
model: the one that lets an outside assistant author FUSE against the engine's
**ground truth**.

Two properties make it safe to hand an assistant:

* **Every answer is the engine's, exactly.** Each tool runs Oxyde's own `oxtool`
  and returns what it says — never a model's paraphrase. Ask it whether a move
  connects and it performs the move in the engine and reports what happened.
* **Read-only, always.** Nothing here writes, repairs or deletes content. The
  write-side tools are deliberately not exposed — an assistant should *propose* a
  change for you to apply, not mutate your characters behind a tool call.

It carries no model and no data of its own: it is a thin protocol adapter over
tools that already ship with the engine, and it runs entirely on your machine —
there is no network.

## What it exposes

| Tool | What it answers |
|---|---|
| `ask` | Retrieval over Oxyde's documentation and its casebook of real faults — "how does X work in Oxyde?" |
| `transpile_fuse` | Transpile a CNS or ZSS file to readable FUSE — exact and deterministic |
| `moves` | Perform a character's moves headlessly; which fire, which connect, at what range and for how much |
| `info` | The derived facts about one character, read from its data |
| `audit` | How much of a character actually works, measured in the engine |
| `verify` | Load every character and stage in a folder; report what fails and why |
| `fusediff` | Compare each converted `X.fuse` against its original; catch a lossy conversion |
| `troubleshoot` | Explain *why* a character shows a symptom ("it froze", "it cannot be hit"), read from its own files |
| `find_freeze` | Detect whether a character traps itself in a state it never leaves, and name it — detection only, never a fix |

## Install

The release ships the server beside the engine: `oxyde-mcp` (or `oxyde-mcp.exe`)
sits in `release-artifacts/<platform>/`, next to `oxtool`. Put the two somewhere
on your machine — keeping them together is enough for `oxyde-mcp` to find
`oxtool`.

Or build it from source, if you have the engine's repository:

```
cargo build --release -p oxyde-mcp
```

The binary lands at `target/release/oxyde-mcp`.

## Configure a client

`oxyde-mcp` is a stdio server: the client launches the binary and talks to it
over its pipes. Point your client at the binary and, optionally, set two
environment variables:

* `OXYDE_OXTOOL` — the path to `oxtool`. Defaults to an `oxtool` sitting beside
  `oxyde-mcp`, else `oxtool` on your `PATH`.
* `OXYDE_ROOT` — a default Oxyde installation folder, so the tools that take a
  game root (`moves`, `info`, `audit`, `verify`, `fusediff`, `troubleshoot`,
  `find_freeze`) need not be told it
  on every call.

Most MCP clients use a configuration of this shape:

```json
{
  "mcpServers": {
    "oxyde": {
      "command": "/path/to/oxyde-mcp",
      "env": {
        "OXYDE_OXTOOL": "/path/to/oxtool",
        "OXYDE_ROOT": "/path/to/your/oxyde/installation"
      }
    }
  }
}
```

After it is configured, the assistant has the tools above available and can, for
example, answer "does Kung Fu Man's `qcf+p` actually connect, and for how much?"
by *running* the move rather than reasoning about the script.

## Check it by hand

The stdio transport is just lines of JSON, so you can drive it with no client at
all:

```
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"ask","arguments":{"query":"what does HitDef attr mean"}}}' \
  | OXYDE_OXTOOL=./oxtool ./oxyde-mcp
```

The first line initialises the session, the second lists the tools, the third
asks a question — each answered with a line of JSON back.

## Why read-only

An assistant that can *see* everything about your content and *change* nothing is
the right trade. It can read the docs, transpile a file to show you the FUSE,
measure whether a character works, and diff a conversion — all the understanding,
none of the risk. When it concludes a file needs converting or repairing, it
tells you the command to run (`oxtool fuse`, `oxtool normalize`), and you apply
it. See [TOOLS.md](TOOLS.md) for those commands, and [FUSE.md](FUSE.md) for the
language the assistant helps you write.
