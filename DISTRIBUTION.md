# ShareXtract Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains the canonical source; third-party registries are discovery/install surfaces, not independent source copies.

## Canonical identity

- Repository: `wuaishare/sharextract`
- Skill path: `/SKILL.md`
- Runtime package: `sharextract`
- Canonical repository license: Apache-2.0
- Current release: `v0.23.4`
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
| ClawHub | Registry publish | **Published/latest:** https://clawhub.ai/wuaishare/sharextract — `0.23.4`, MIT-0, 5-file authored thin Skill bundle. A server-side `--update` scan completed with A.I.G `clean / 0 findings`, ClawScan `clean / benign / high`, SkillSpector `0 / LOW / SAFE`, and Static Analysis `clean / 0 findings`; VirusTotal was unavailable. `clawhub skill verify` passes the security gate and is currently blocked only by platform-generated `skill-card.md` still being unavailable. Manual publish provenance remains `unavailable`, so ClawHub must not be presented as having verified the GitHub source anchor. Historical versions are retained for auditability; `latest` points to 0.23.4. |
| AI智库 | First-party catalog | **Published:** https://ai.wuaishare.cn/hub/sharextract/ — richer GitHub/i18n/security enrichment is tracked as a catalog pipeline improvement |

## ClawHub verification evidence

- Verified version: `0.23.4`
- Source fingerprint: `7327d3df5eb16c92900cbad6c4586dc3b9631fefcc53122afdeb93ed6d343d2d`
- Full server-side scan ID: `w174305g4pf3xt0m6xttecfcqs8e3yra`
- Scan completed: `2026-09-09T16:42:00+08:00`
- Write-back: `true`
- A.I.G `0.2.1`: `clean`, 0 findings
- ClawScan: `clean`, `benign`, high confidence; all install/instruction/persistence/purpose dimensions are `ok` except the expected network/runtime environment note
- SkillSpector `2.3.5`: score `0`, severity `LOW`, recommendation `SAFE`, 0 issues
- Static Analysis `v2.4.26`: `clean`, 0 findings
- VirusTotal: unavailable for this scan; do not represent this as a clean VirusTotal verdict
- `clawhub skill verify`: security gate passes; the overall verifier remains temporarily blocked by `card.missing` until ClawHub generates its server-side `skill-card.md`
- ClawHub signature: `unsigned`
- ClawHub provenance: `unavailable` for this manually published version; the canonical GitHub v0.23.4 release separately provides a reproducible wheel, `SHA256SUMS`, and GitHub provenance attestation
- Note: the scan API response includes the A.I.G result, while the current downloaded report ZIP does not yet contain a separate `aig.json`; treat the API response as the A.I.G evidence source until ClawHub's ZIP export format catches up

## Rules

1. Do not fork the Skill text per marketplace unless a platform requires a thin packaging adapter.
2. Never change the canonical repository license merely to satisfy a registry without an explicit project decision.
3. Marketplace metadata must point back to the canonical repository and exact Skill path.
4. Version, license, install requirements, security boundaries, and last verification time should remain machine-readable where the platform supports them.
5. ClawHub publishes only the portable Skill layer; the Python runtime remains canonical on GitHub under Apache-2.0.
6. A marketplace listing is a distribution surface, not proof of security or quality; ShareXtract's tests, Adapter Health, provenance and release gates remain the primary evidence.
7. Published core wheel assets are append-only by policy: never overwrite an existing release asset; cut a new patch release when runtime bits, build metadata, or the pinned digest changes.
