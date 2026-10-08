# Sylvex Brain v2

An isolated rebuild of the Sylvex Brain orchestration layer.

## Design

- Voice: outward conversational interface
- Memory: persistent context with explicit thread boundaries
- Distillation: durable memory separate from raw transcripts
- Sylvex: native vocabulary/grammar interface
- AI↔AI bridge: bounded external-model exchanges
- Living Record: append-only exchange history
- Protocol chamber: experimental/test execution kept separate from ordinary chat
- NativeLM: experimental substrate retained as an optional layer

This directory is intentionally isolated from the existing Brain implementation and from the main Cradle site.
