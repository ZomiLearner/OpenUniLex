# **Parser integration with OpenUniLex** 

It is straightforward once you understand the flow: the parser doesn’t “guess” how to interpret lexemes — it *delegates all structural decisions to OpenUniLex’s schemas*. This gives you a stable, language‑agnostic, UPOS‑aware lexical backbone for any NLP system.

Below is a complete, structured explanation of how a parser integrates with OpenUniLex, from loading lexemes to building internal models.

---

## **1. The Core Idea: The Parser Treats OpenUniLex as the Lexical Authority**

Your parser does **not** define what a lexeme looks like.  
It does **not** define morphology.  
It does **not** define valency.  
It does **not** define UPOS constraints.

All of that comes from **OpenUniLex**.

The parser simply:

1. **Loads lexeme files**  
2. **Routes them through the master schema**  
3. **Validates them against shared + UPOS schemas**  
4. **Builds internal lexical objects**  
5. **Uses those objects during parsing**

This makes OpenUniLex the *single source of truth* for lexical structure.

---

## **2. Integration Pipeline (High‑Level)**

### **Step 1 — Load lexeme JSON**

The parser reads one lexeme file at a time.

### **Step 2 — Route via master schema**

The master schema determines:

- UPOS category  
- which shared schemas apply  
- which UPOS profile applies  
- which schema versions to load  

### **Step 3 — Validate**

The parser uses OpenUniLex’s schema files to validate the lexeme.

### **Step 4 — Normalize**

The parser converts the lexeme JSON into a structured internal object.

### **Step 5 — Use in parsing**

The parser uses the lexeme’s:

- morphology  
- valency  
- semantics  
- IGT examples  
- metadata  

to guide tokenization, tagging, dependency parsing, and semantic interpretation.

---

## **3. Integration Diagram**

Below is a conceptual diagram of the integration flow.

---

## **4. What the Parser Actually Imports**

The parser imports:

- **master schema**  
- **shared schemas**  
- **UPOS profiles**  
- **lexeme files**  

It does *not* import:

- raw linguistic rules  
- language‑specific hacks  
- custom morphology tables  

Everything comes from OpenUniLex.

---

## **5. Internal Parser API Structure**

### **LexemeLoader**

Loads and parses lexeme JSON.

### **SchemaRouter**

Uses `master.schema.json` to determine which schema chain applies.

### **SchemaValidator**

Validates lexemes against the correct schema versions.

### **LexemeObject**

The normalized internal representation used by the parser.

### **LexiconManager**

Caches lexemes, supports lazy loading, and provides lookup functions.

---

## **6. Example Integration Flow**

### **Parser loads lexeme file**

```bash
lexicons/en/verb/run.json
```

### **Parser routes lexeme**

Master schema says:

- UPOS = VERB  
- Use `verb.schema.json`  
- Use shared morphology + valency schemas  

### **Parser validates lexeme**

If validation fails → parser rejects lexeme.

### **Parser builds internal object**

```ts
LexemeObject {
    lemma: "run",
    upos: "VERB",
    morphology: { ... },
    valency: { ... },
    semantics: { ... }
}
```

### **Parser uses lexeme during parsing**

- morphological tagging  
- dependency prediction  
- valency enforcement  
- semantic role assignment  

---

## **7. How Parsers Benefit from OpenUniLex**

### **✔ Consistency across languages**

Same schema → same structure → same parser logic.

### **✔ No custom per‑language hacks**

All constraints live in UPOS profiles.

### **✔ Rich lexical information**

Valency, morphology, semantics, IGT examples.

### **✔ Version stability**

Lexemes declare the schema version they follow.

### **✔ Atomic lexemes**

Easy to load, validate, update, and cache.

---

## **8. Recommended Parser Features**

Your parser should support:

- **lazy lexeme loading**  
- **lexeme caching**  
- **schema version pinning**  
- **batch lexicon loading**  
- **multilingual lexicon directories**  

These make integration smooth and scalable.

---

## **9. Integration Summary Table**

| Component | Role | Parser Responsibility |
|----------|------|------------------------|
| **Master schema** | Routes lexemes | Load + apply |
| **Shared schemas** | Core structure | Validate |
| **UPOS profiles** | Domain constraints | Validate |
| **Lexeme files** | Lexical data | Load + normalize |
| **LexemeObject** | Internal model | Use in parsing |
| **Versioning** | Stability | Pin + warn |

---

## **Final takeaway**

**OpenUniLex is not just a lexicon — it is the parser’s lexical brain.**  
Your parser becomes simpler, more consistent, and more multilingual by delegating all lexical structure to OpenUniLex.

---
