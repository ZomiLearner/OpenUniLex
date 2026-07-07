# **Schema Migration Guide — OpenUniLex**

Schema migrations ensure that lexemes remain valid and parsers remain stable as OpenUniLex evolves. This guide explains how to migrate lexemes and tools when schema versions change, how to detect breaking changes, and how to use the schema registry to automate migration workflows.

---

## **🎯 Purpose of This Guide**

This document helps contributors and parser developers:

- understand when migration is required  
- follow a predictable migration workflow  
- update lexemes safely  
- update tools and validators  
- interpret changelog entries  
- use the schema registry to automate version transitions  

---

## **📌 When Migration Is Required**

Migration is required **only** when a schema introduces a **MAJOR** version change.

Examples of breaking changes:

- removing a field  
- renaming a field  
- changing a field’s type  
- changing required → optional or optional → required  
- altering UPOS routing logic  
- removing or restructuring shared components  

Migration is **not** required for:

- MINOR updates (new optional fields)  
- PATCH updates (fixes, clarifications, examples)  

See **semantic versioning** for details.

---

## **🧭 Migration Workflow Overview**

The migration workflow has five steps:

1. **Identify the schema change**  
2. **Read the relevant `CHANGELOG.md`**  
3. **Check the lexeme’s declared schema versions**  
4. **Apply migration rules**  
5. **Validate using updated tools**

Each step is explained below.

---

## **1. Identify the Schema Change**

Schema changes are announced in:

- `schemas/index.json`  
- each schema family’s `CHANGELOG.md`  
- release notes (optional)

Use the registry to detect new versions:

```json
{
  "master": {
    "default": "1.1.0",
    "versions": {
      "1.0.0": "master/v1.0.0.master.schema.json",
      "1.1.0": "master/v1.1.0.master.schema.json"
    }
  }
}
```

Tools should compare lexeme version declarations against the registry.

---

## **2. Read the Schema’s CHANGELOG**

Each schema family has its own changelog:

- `schemas/master/CHANGELOG.md`  
- `schemas/shared/base_properties/CHANGELOG.md`  
- `schemas/upos/verb/CHANGELOG.md`  

Changelogs tell you:

- what changed  
- whether migration is required  
- how lexemes are affected  
- whether parsers must update their routing logic  

If migration is required, the changelog will include a section like:

```text
### Migration required: yes
```

---

## **3. Check the Lexeme’s Declared Schema Versions**

Every lexeme declares the schema versions it follows:

```json
{
  "schema": {
    "master": "1.0.0",
    "upos": "verb",
    "profile_version": "1.0.0"
  }
}
```

Migration is required if:

- the lexeme uses an older MAJOR version  
- the schema family has a newer MAJOR version  
- the changelog indicates breaking changes  

Tools can detect this automatically.

---

## **4. Apply Migration Rules**

Migration rules come from:

- the schema’s `CHANGELOG.md`  
- optional `MIGRATION.md` files  
- tooling notes in the changelog  

### **Typical migration actions**

- **Rename fields**  
  Example: `orth` → `orthography`

- **Move fields**  
  Example: moving `dialect_tag` from base_properties to metadata

- **Add required fields**  
  Example: new required `semantic_domain`

- **Remove deprecated fields**  
  Example: removing `legacy_tag`

- **Update field types**  
  Example: `Number: "Sing"` → `Number: ["Sing"]`

- **Update UPOS routing**  
  Example: verbs now require a `valency` array

### **Migration example**

Before:

```json
{
  "orth": "dog"
}
```

After:

```json
{
  "orthography": "dog"
}
```

---

## **5. Validate Using Updated Tools**

After applying migration rules:

- run validators in `tools/validators/`  
- ensure lexeme passes master + shared + UPOS validation  
- ensure schema versions are updated in the lexeme  
- ensure no deprecated fields remain  

Validators should:

- warn on deprecated fields  
- fail on removed fields  
- auto‑fix simple migrations (optional)  

---

## **🧩 Migration Checklist**

### **For lexeme authors**

- Check schema version  
- Read changelog  
- Apply migration rules  
- Validate lexeme  

### **For parser developers**

- Update schema loader  
- Update routing logic  
- Update internal LexemeObject  
- Run integration tests  

---

## **📦 Optional: MIGRATION.md per schema**

For complex schema families, add:

```bash
schemas/shared/base_properties/MIGRATION.md
```

Contents:

- migration examples  
- before/after lexeme snippets  
- tooling notes  
- parser notes  

This is optional but extremely helpful.

---

## **📚 Appendix: Migration Examples**

### **MAJOR update example**

```bash
## 2.0.0 — 2026-10-01
- Removed deprecated field `legacy_tag`
- Renamed `orth` → `orthography`
- Added required field `semantic_domain`
- Migration required: yes
```

Lexeme migration:

Before:

```json
{
  "orth": "run",
  "legacy_tag": "old"
}
```

After:

```json
{
  "orthography": "run",
  "semantic_domain": "motion"
}
```

---

## **Final takeaway**

Schema migration in OpenUniLex is predictable, structured, and tool‑friendly.  
This guide ensures lexemes remain stable and parsers remain compatible across schema evolution.
