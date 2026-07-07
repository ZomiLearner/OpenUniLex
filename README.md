# **OpenUniLex**

## *Universal Open Lexicon Framework for Multilingual NLP*

**OpenUniLex** is an open, language‑agnostic framework for building, validating, and sharing lexicon entries across any language. It provides a comprehensive schema system, atomic lexeme files, validation tools, and UPOS‑aware structural constraints — all in a single unified monorepo designed to serve as a core dependency for NLP parsers and linguistic tooling.

---

## **✨ Key Features**

- **Universal schema architecture** powered by a master router and UPOS‑specific profiles  
- **One lexeme per file** for atomic versioning, clean diffs, and modular validation  
- **Shared linguistic components** (morphology, valency, metadata, IGT)  
- **Multilingual lexicon directories** for parallel language development  
- **Schema versioning** with SemVer and per‑schema changelogs  
- **Tooling suite** for validation, conversion, and lexeme generation  
- **Parser‑ready design** — OpenUniLex is built to be consumed by NLP parsers directly  

---

## **📁 Repository Structure**

```bash
OpenUniLex/
│
├── schemas/
│   ├── master/
│   │   ├── v1.0.0.master.schema.json
│   │   └── CHANGELOG.md
│   │
│   ├── shared/
│   │   ├── base_properties/
│   │   ├── metadata/
│   │   ├── valency_arguments/
│   │   └── igt_example/
│   │
│   └── upos/
│       ├── noun/
│       ├── verb/
│       ├── modifier/
│       ├── functional/
│       └── grammar_glue/
│
├── lexicons/
│   ├── en/
│   ├── hi/
│   ├── ar/
│   └── ...
│
├── tools/
│   ├── validators/
│   ├── converters/
│   └── generators/
│
├── examples/
│   ├── minimal_entry.json
│   └── bilingual_pair.json
│
└── docs/
    ├── schema-guide.md
    ├── lexicon-guide.md
    └── architecture.md
```

---

## **🧱 Schema Architecture Overview**

OpenUniLex uses a modular schema system:

### **1. Master Schema Router**

Routes lexemes using UPOS‑based `if/then` logic.

### **2. Shared Components**

Reusable structures for:

- **Base properties**  
- **Metadata**  
- **UD morphology**  
- **Valency arguments**  
- **IGT examples**  

### **3. UPOS Profiles**

Domain‑specific constraints for:

- **Nouns**  
- **Verbs**  
- **Modifiers**  
- **Functional words**  
- **Grammar glue**  

This structure ensures consistency across languages while allowing fine‑grained linguistic detail.

---

## **📄 Lexeme Format (One Lexeme Per File)**

Each lexeme is an atomic JSON document:

```json
{
  "schema": {
    "master": "1.0.0",
    "upos": "noun",
    "profile_version": "1.0.0"
  },

  "lemma": "dog",
  "orth": "dog",
  "dialect_tag": "en-general",

  "morphology": {
    "Number": "Sing"
  },

  "valency": [],
  "igt_example": {
    "text": "The dog barked.",
    "gloss": "DET dog bark.PST"
  },

  "metadata": {
    "annotator": "user123",
    "timestamp": "2026-07-06T02:48:00Z",
    "status": "draft"
  }
}
```

---

## **🔧 Tooling**

OpenUniLex includes tools for:

- **Lexeme validation** against master + shared + UPOS schemas  
- **Schema version management**  
- **Lexeme template generation**  
- **Format conversion** (CSV → JSON, etc.)  

Tools are designed to integrate directly with parser libraries.

---

## **🧩 Using OpenUniLex in an NLP Parser**

Parsers can:

- Load lexeme files  
- Route them through the master schema  
- Validate them against shared + UPOS schemas  
- Build internal lexical models  
- Support multilingual parsing  

See **parser integration guide** for details.

---

## **🌍 Multilingual Support**

OpenUniLex supports any language.  
Each language gets its own directory under `lexicons/`.

You can add new languages by creating:

```bash
lexicons/<lang-code>/
```

and adding lexeme files inside.

---

## **📜 Versioning Policy**

Schemas follow **Semantic Versioning (SemVer)**:

- **MAJOR** — breaking changes  
- **MINOR** — new optional fields  
- **PATCH** — fixes and clarifications  

Each schema folder contains its own [CHANGELOG.md](./CHANGELOG.md).

Lexemes declare the schema version they follow.

---

## **🤝 Contributing**

Contributions are welcome from:

- linguists  
- NLP researchers  
- parser developers  
- language communities  

See **[contributing.md](docs/contributing.md)** for guidelines.

---

## **📣 License**

OpenUniLex is fully open‑source.  
See [LICENSE](./LICENSE) for details.

---
