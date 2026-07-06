# **OpenUniLex Contribution Guide**

OpenUniLex is a universal, open‑source lexicon framework. Contributions from linguists, developers, and language communities are essential to expanding its multilingual coverage and improving its schema architecture.

This guide explains how to contribute safely, consistently, and effectively.

---

## **🌱 Ways You Can Contribute**

- **Add new lexemes**  
- **Add a new language directory**  
- **Improve or propose schemas**  
- **Submit validation or conversion tools**  
- **Fix bugs or improve documentation**  
- **Discuss design decisions**  

All contributions are welcome — from small fixes to major structural improvements.

---

## **📁 Repository Structure Overview**

Understanding the repo layout helps you contribute correctly:

```
OpenUniLex/
├── schemas/        # Master router, shared components, UPOS profiles
├── lexicons/       # One lexeme per file, grouped by language
├── tools/          # Validators, converters, generators
├── examples/       # Sample lexemes and bilingual pairs
└── docs/           # Guides, architecture notes, versioning policy
```

---

## **🧱 Adding a New Lexeme**

### **1. Choose the correct language directory**

Example:

```bash
lexicons/en/
lexicons/hi/
lexicons/ar/
```

If the language doesn’t exist yet, see **Add a new language directory**.

### **2. Create one JSON file per lexeme**

Example:

```bash
lexicons/en/noun/dog.json
```

### **3. Follow the schema**

Each lexeme must include:

- `schema.master` version  
- `schema.upos` category  
- `schema.profile_version`  
- core fields (lemma, orth, dialect_tag)  
- morphology  
- valency  
- metadata  
- optional IGT example  

### **4. Validate your lexeme**

Use the validator in:

```bash
tools/validators/
```

### **5. Submit a pull request**

Include:

- the lexeme file  
- a short description  
- any linguistic notes  

---

## **🌍 Adding a New Language Directory**

To add a new language:

1. Create a folder under `lexicons/` using ISO‑639‑1 or ISO‑639‑3 codes  
2. Add a `README.md` describing the language  
3. Add at least one lexeme  
4. Validate all entries  
5. Submit a pull request

Example:

```bash
lexicons/yo/
    README.md
    noun/
        ile.json
```

---

## **🧬 Proposing Schema Changes**

Schema changes must be carefully reviewed because they affect all languages.

### **Steps:**

1. Open an issue describing the change  
2. Explain why it’s needed  
3. Provide examples of lexemes affected  
4. Propose a version bump (SemVer)  
5. Update the relevant `CHANGELOG.md`  
6. Submit a PR with the updated schema file  

Schemas live in:

```bash
schemas/master/
schemas/shared/
schemas/upos/
```

---

## **🔧 Contributing Tools**

Tools must be:

- language‑agnostic  
- schema‑aware  
- safe for batch processing  
- compatible with versioned schemas  

Place tools under:

```bash
tools/validators/
tools/converters/
tools/generators/
```

Include documentation in `docs/`.

---

## **📚 Improving Documentation**

You can contribute by:

- clarifying schema behavior  
- adding examples  
- improving guides  
- documenting tools  
- writing tutorials  

Documentation lives in:

```bash
docs/
```

---

## **🧪 Testing Your Contributions**

Before submitting a PR:

- run schema validation  
- run lexeme validation  
- ensure JSON formatting is consistent  
- ensure schema `$ref` paths are correct  
- ensure no breaking changes without version bumps  

---

## **🤝 Pull Request Guidelines**

Your PR should include:

- a clear description  
- reasoning behind the change  
- validation results  
- updated changelog (if schema changes)  
- examples (if relevant)  

PRs are reviewed for:

- correctness  
- schema compliance  
- linguistic accuracy  
- clarity  
- maintainability  

---

## **📣 Community Standards**

OpenUniLex follows these principles:

- Be respectful  
- Be precise  
- Be collaborative  
- Be multilingual‑friendly  
- Be open to revision  

We welcome contributions from all language communities.

---
