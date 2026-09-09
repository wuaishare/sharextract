# ShareXtract Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains the canonical source; third-party registries are discovery/install surfaces, not independent source copies.

## Canonical identity

- Repository: `wuaishare/sharextract`
- Skill path: `/SKILL.md`
- Runtime package: `sharextract`
- Canonical repository license: Apache-2.0
- Current release: `v0.23.3`
- Version source of truth: `pyproject.toml` + GitHub Releases
- Core release integrity: reproducible `py3-none-any` wheel + `SHA256SUMS` + GitHub provenance attestation; `SKILL.md` records the expected runtime version and wheel SHA-256 but never installs software autonomously
- Agent Skills metadata: `SKILL.md` uses the portable `license`, `compatibility`, and `metadata.author/version` fields

## Distribution matrix

| Surface | Repository policy | Current integration mode |
| --- | --- | --- |
| skills.sh | GitHub-native | Install with `npx skills add wuaishare/sharextract`; repository is canonical |
| SkillsMP | GitHub-indexed | Eligible for automated discovery through Agent Skill metadata and GitHub topics |
| AgentSkill.sh | Registry import/sync | Imported from the canonical `SKILL.md`; security score 100/100. GitHub owner-level re-import/claim remains blocked by the registry's server-side GitHub API rate limit (HTTP 429) |
| skills.re | GitHub import | **Publicly indexed:** https://skills.re/skills/wuaishare/sharextract/sharextract under Wuaishare, with registry-generated Python / Information-Retrieval / API-Integration tags |
| Skillstore | GitHub URL + independent audit | Original submission `c3bdf489-27cd-4c45-b40c-d1c94d494de9` produced PR #3323 and a high-risk report against an older commit. Those findings drove upstream SSRF/browser/prompt-injection hardening and v0.23.1. A public re-submit now collides with the existing `pending/wuaishare/sharextract` target, so re-audit has been requested in aiskillstore/marketplace issue #3324 |
| Smithery Skills | Git-backed/API listing | **Published/listed:** https://smithery.ai/skills/wuaishare/sharextract, backed by the canonical GitHub repository |
| ClawHub | Registry publish | **Published/latest:** https://clawhub.ai/wuaishare/sharextract — `0.23.1`, MIT-0, thin Skill bundle. ClawHub moderation is clean and the version-level LLM scanner is clean/benign after the runtime install was pinned to the immutable v0.23.1 release commit. The accidental `0.1.0` full-repository import and superseded `0.23.0` version have been withdrawn |
| AI智库 | First-party catalog | **Published:** https://ai.wuaishare.cn/hub/sharextract/ — richer GitHub/i18n/security enrichment is tracked as a catalog pipeline improvement |

## Rules

1. Do not fork the Skill text per marketplace unless a platform requires a thin packaging adapter.
2. Never change the canonical repository license merely to satisfy a registry without an explicit project decision.
3. Marketplace metadata must point back to the canonical repository and exact Skill path.
4. Version, license, install requirements, security boundaries, and last verification time should remain machine-readable where the platform supports them.
5. ClawHub publishes only the portable Skill layer; the Python runtime remains canonical on GitHub under Apache-2.0.
6. A marketplace listing is a distribution surface, not proof of security or quality; ShareXtract's tests, Adapter Health, provenance and release gates remain the primary evidence.
7. Published core wheel assets are append-only by policy: never overwrite an existing release asset; cut a new patch release when runtime bits, build metadata, or the pinned digest changes.
