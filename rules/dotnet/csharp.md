---
paths:
  - "**/*.cs"
description: Structured-log placeholder and cancellation rules for C# code.
owner: skills/universal/software-csharp-backend/SKILL.md
---
Extends common/errors.md.
- Name Serilog message-template placeholders in PascalCase, with no dots: `{DeviceId}`, not `{Device.Id}`.
- Accept a `CancellationToken` at each cancellable request and worker boundary, and pass it to every database, HTTP, queue, and delay call.
- Never turn a client disconnect or deadline expiry into a generic 500.
- Enforce token forwarding in the project's CI with analyser CA2016.
Why and procedure: skills/universal/software-csharp-backend/SKILL.md#do--avoid
