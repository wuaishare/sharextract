# ShareXtract Distribution

This document is the repository-level source of truth for Agent Skill distribution. The GitHub repository remains the canonical source; third-party registries are discovery/install surfaces, not independent source copies.

## Canonical identity

- Repository: `wuaishare/sharextract`
- Skill path: `/SKILL.md`
- Runtime package: `sharextract`
- License: Apache-2.0
- Version source of truth: `pyproject.toml` + GitHub Releases

## Distribution matrix

| Surface | Repository policy | Current integration mode |
| --- | --- | --- |
| skills.sh | GitHub-native | Install with `npx skills add wuaishare/sharextract`; repository is canonical |
| SkillsMP | GitHub-indexed | Eligible for automated discovery through Agent Skill metadata and GitHub topics |
| AgentSkill.sh | GitHub import/sync | Ready for owner-verified GitHub import; registry account connection is external to this repository |
| Smithery Skills | Git-backed/API listing | Ready for listing; Smithery namespace/API authorization is required to publish |
| ClawHub | Registry publish | **Not published**: ClawHub applies MIT-0 to published skills, which conflicts with this repository's Apache-2.0 license unless a deliberate separate licensing/package decision is made |
| AI智库 | First-party catalog | Canonical first-party listing should point back to this repository and preserve provenance/version/license metadata |

## Rules

1. Do not fork the Skill text per marketplace unless a platform requires a thin packaging adapter.
2. Never change the repository license merely to satisfy a registry without an explicit project decision.
3. Marketplace metadata must point back to the canonical repository and exact Skill path.
4. Version, license, install requirements, security boundaries, and last verification time should remain machine-readable where the platform supports them.
5. A marketplace listing is a distribution surface, not proof of security or quality; ShareXtract's tests, Adapter Health, provenance and release gates remain the primary evidence.
