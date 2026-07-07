# **CHANGELOG Template for OpenUniLex Schemas**


## CHANGELOG — <schema‑name> schema

This file documents all notable changes to the <schema‑name> schema.
Schema versioning follows Semantic Versioning (MAJOR.MINOR.PATCH).

---

## [Unreleased]
- Proposed changes not yet released.
- Add new entries here before tagging a version.

---

## <version> — <YYYY‑MM‑DD>
### Type: <MAJOR | MINOR | PATCH>

### Summary
- Brief description of what changed and why.

### Changes
- Added: …
- Removed: …
- Modified: …
- Deprecated: …
- Fixed: …

### Impact
- Breaking changes: <yes/no>
- Migration required: <yes/no>
- Notes for lexeme authors: …
- Notes for parser developers: …

### Migration Guide (if applicable)
- Step‑by‑step instructions for updating lexemes.
- Example before/after snippets.
- Tooling notes (validators, converters, generators).

---

## 1.0.0 — 2026‑07‑06
### Type: MAJOR
### Summary
- Initial release of the <schema‑name> schema.

### Changes
- Introduced core fields.
- Established baseline constraints.
- Added initial validation rules.

### Impact
- No migration required (first release).

```

## 📁 Where to place this template

Use this template in each schema directory:

- `schemas/master/CHANGELOG.md`  
- `schemas/shared/base_properties/CHANGELOG.md`  
- `schemas/shared/metadata/CHANGELOG.md`  
- `schemas/upos/verb/CHANGELOG.md`  
- etc.

---
