# ShareXtract Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains the canonical source; third-party registries are discovery/install surfaces, not independent source copies.

## Canonical identity

- Repository: `wuaishare/sharextract`
- Skill path: `/SKILL.md`
- Runtime package: `sharextract`
- Canonical repository license: Apache-2.0
- Version source of truth: `pyproject.toml` + GitHub Releases
- Agent Skills metadata: `SKILL.md` uses the portable `license`, `compatibility`, and `metadata.author/version` fields

## Distribution matrix

| Surface | Repository policy | Current integration mode |
| --- | --- | --- |
| skills.sh | GitHub-native | Install with `npx skills add wuaishare/sharextract`; repository is canonical |
| SkillsMP | GitHub-indexed | Eligible for automated discovery through Agent Skill metadata and GitHub topics |
| AgentSkill.sh | Registry import/sync | Imported from the canonical `SKILL.md`; security score 100/100. GitHub owner-level re-import/claim remains blocked by the registry's GitHub API rate limit |
| skills.re | GitHub import | Submitted from the canonical repository; processing/listing is asynchronous |
| Skillstore | GitHub URL + audit PR | Submitted as `c3bdf489-27cd-4c45-b40c-d1c94d494de9`; automated processing/audit is in progress |
| Smithery Skills | Git-backed/API listing | Ready for listing; Smithery account/namespace authorization is still required |
| ClawHub | Registry publish | **Published:** https://clawhub.ai/wuaishare/sharextract — initial web import is MIT-0. A corrected `0.23.0` thin bundle is prepared; `.clawhubignore` limits future releases to `SKILL.md` + four referenced files while the Python runtime remains Apache-2.0 on GitHub |
| AI智库 | First-party catalog | **Published:** https://ai.wuaishare.cn/hub/sharextract/ — richer GitHub/i18n/security enrichment is tracked as a catalog pipeline improvement |

## Rules

1. Do not fork the Skill text per marketplace unless a platform requires a thin packaging adapter.
2. Never change the canonical repository license merely to satisfy a registry without an explicit project decision.
3. Marketplace metadata must point back to the canonical repository and exact Skill path.
4. Version, license, install requirements, security boundaries, and last verification time should remain machine-readable where the platform supports them.
5. ClawHub publishes only the portable Skill layer; the Python runtime remains canonical on GitHub under Apache-2.0.
6. A marketplace listing is a distribution surface, not proof of security or quality; ShareXtract's tests, Adapter Health, provenance and release gates remain the primary evidence.
