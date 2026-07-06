# **OpenUniLex Schema Versioning Policy**

This policy defines how schema versions are created, updated, documented, and consumed across the OpenUniLex ecosystem. It ensures stability for lexicon contributors, NLP parser developers, and downstream tools.

---

## **1. Versioning Model: Semantic Versioning (SemVer)**

All schemas in OpenUniLex follow **Semantic Versioning**:

```bash
MAJOR.MINOR.PATCH
```

### **MAJOR (X.0.0)**

Breaking changes that require lexeme updates or parser adjustments.

Examples:

- Removing a field
- Renaming a field  
- Changing a field’s type  
- Changing required → optional or optional → required  
- Changing UPOS routing logic  

### **MINOR (X.Y.0)**

Backward‑compatible enhancements.

Examples:

- Adding new optional fields
- Adding new shared components  
- Adding new UPOS‑specific constraints that do not break existing lexemes  

### **PATCH (X.Y.Z)**

Backward‑compatible fixes.

Examples:

- Clarifying descriptions  
- Fixing typos  
- Adjusting regex patterns  
- Improving examples  

---

## **2. Versioning Scope**

Each schema is versioned **independently**, not the entire repo.

This means:

- `master.schema.json` has its own version history  
- each shared schema has its own version history  
- each UPOS profile has its own version history  

This allows parallel evolution without forcing global updates.

---

## **3. Versioned File Naming**

Each schema version is stored as a separate file:

```bash
schemas/
    master/
        v1.0.0.master.schema.json
        v1.1.0.master.schema.json
    shared/
        base_properties/
            v1.0.0.base_properties.schema.json
        metadata/
            v1.0.0.metadata.schema.json
    upos/
        verb/
            v1.0.0.verb.schema.json
            v1.1.0.verb.schema.json
```

This ensures:

- stable `$ref` paths  
- reproducible builds  
- safe long‑term lexicon storage  

---

## **4. Lexeme Schema Declaration**

Every lexeme must declare the schema versions it follows:

```json
{
  "schema": {
    "master": "1.1.0",
    "upos": "verb",
    "profile_version": "1.0.0"
  }
}
```

This allows:

- parsers to validate correctly  
- lexemes to remain valid across schema evolution  
- contributors to update lexemes only when necessary  

---

## **5. Changelog Requirements**

Each schema folder must contain a `CHANGELOG.md` documenting:

- version number  
- date  
- type of change (MAJOR, MINOR, PATCH)  
- description  
- migration notes (if applicable)  

Example:

```bash
## 1.1.0 — 2026-07-06
- Added optional field `semantic_domain`
- No migration required
```

---

## **6. Breaking Change Protocol (MAJOR Updates)**

When proposing a breaking change:

1. Open an issue describing the change  
2. Provide examples of affected lexemes  
3. Propose a migration plan  
4. Update the schema file  
5. Update the changelog  
6. Increment MAJOR version  
7. Provide a migration script (optional)  

Breaking changes must be reviewed by maintainers and community contributors.

---

## **7. Deprecation Policy**

Fields may be deprecated before removal.

Deprecation steps:

1. Mark field as `"deprecated": true` in schema  
2. Add a note in the changelog  
3. Provide a recommended replacement  
4. Remove the field in the next MAJOR version  

This gives contributors time to update lexemes safely.

---

## **8. Parser Compatibility**

Parsers may:

- pin to specific schema versions  
- support multiple schema versions simultaneously  
- warn when lexemes use outdated versions  
- refuse lexemes using deprecated MAJOR versions  

This ensures stability for downstream NLP systems.

---

## **9. Version Registry**

OpenUniLex maintains a registry file:

```bash
schemas/index.json
```

Example:

```json
{
  "master": ["1.0.0", "1.1.0"],
  "shared": {
    "base_properties": ["1.0.0"],
    "metadata": ["1.0.0"]
  },
  "upos": {
    "verb": ["1.0.0", "1.1.0"],
    "noun": ["1.0.0"]
  }
}
```

This helps tools discover available versions.

---

## **10. Tooling Requirements**

Validators and generators must:

- load schema versions dynamically  
- support multiple versions  
- warn on deprecated versions  
- fail on invalid version references  

This ensures lexicon integrity across the ecosystem.

---
