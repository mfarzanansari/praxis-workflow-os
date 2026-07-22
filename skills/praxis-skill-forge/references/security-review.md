# Agent Skill security review

Treat a skill as a dependency-bearing software artifact whose natural-language metadata can affect discovery, selection, and execution.

## Provenance

- origin repository and canonical URL;
- author/maintainer;
- license;
- version, tag, or commit hash;
- retrieval date;
- checksum or lock record;
- known forks/adaptations.

## Description and instruction review

- Does the description accurately match behavior?
- Does it attempt to trigger broadly or displace other skills?
- Does it instruct the agent to ignore user/system rules?
- Does it conceal side effects behind benign wording?
- Does it load remote or indirect instructions?
- Does it request unnecessary permissions or data?

## Script review

Search for:

- shell/process execution;
- network access and downloads;
- package installation;
- credential/environment access;
- filesystem deletion or replacement;
- obfuscation, encoded payloads, dynamic execution;
- subprocess calls with untrusted input;
- telemetry;
- indirect dependencies and update mechanisms.

## Runtime controls

- least-privilege sandbox;
- no secrets during initial test;
- read-only or disposable workspace;
- network disabled unless required;
- dry-run and explicit confirmation;
- output and filesystem diff inspection;
- pin dependencies and versions.

## Update policy

Review updates as code changes. Do not auto-update third-party skills in a trusted environment without diffing instructions, scripts, references, dependencies, and permissions.
