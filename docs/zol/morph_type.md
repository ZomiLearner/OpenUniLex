# Morphological Type (`morph_type`) Documentation — Zomi (Tedim)

This document establishes the specification and validation rules for the `morph_type` field within the Zomi NLP Lexicon Master Table and Universal Dependencies (UD) treebank pipelines. 

Given that Tedim Zomi is an agglutinative, tonal, and monosyllabic-root language with profound verbal stem alternation and complex predicate compounding, these boundaries ensure computational validation matches actual morphosyntactic realities.

---

## 1. Schema Validation Matrix

The matrix below maps Universal Part-of-Speech (`UPOS`) tags to their permitted `morph_type` values. Any lexical entry violating these pairings will fail the schema validation engine.

| Morphological Type (`morph_type`) | Allowed UPOS Tags | Core Linguistic Characteristic in Zomi |
| :--- | :--- | :--- |
| **`INFLECTIONAL`** | `NOUN`, `VERB`, `ADJ`, `PRON`, `DET`, `NUM`, `AUX`, `ADV` | Undergoes structural, tonal, or stem alternation based on syntactic context. |
| **`DERIVATIONAL`** | `NOUN`, `VERB`, `ADJ`, `ADV`, `NUM` | Uses affixes, clitics, or internal modifications to change word class or core meaning. |
| **`COMPOUND`** | `NOUN`, `VERB`, `ADJ`, `ADV` | Formed by merging two or more autonomous roots/stems into a single lexical unit. |
| **`NONE`** | `ADP`, `CCONJ`, `SCONJ`, `PART`, `INTJ`, `PUNCT`, `SYM` | Invariable, closed-class grammatical particles and structural tokens. |
| **`NON_LINGUISTIC`** | `SYM`, `X` | Mathematical signs, code fragments, emojis, or unclassifiable foreign tokens. |

---

## 2. Zomi-Specific Operational Definitions & Examples

### INFLECTIONAL
Applies to words showing functional modifications. In Zomi, this heavily includes **Verbal Stem Alternation** (Stem I vs. Stem II) and tonal shifts.

*   **`VERB` / `AUX`:** Direct inflection via root alternation.
    *   *Example:* `pia` (Stem I: to give) vs. `piak` (Stem II: gave; give modified).
    *   *Auxiliary Inflection:* Auxiliary verbs like *nuam* (want) or *zo* (manage) alternate stem shapes depending on clause type.
*   **`NOUN`:** Demonstrates inflection via obligatory case/role clitics or markers (e.g., ergative/instrumental *in*, locative *ah*).
*   **`PRON`:** Standard pronominal paradigms (e.g., *keimah*, *ken*). 
    > ⚠️ **Validation Rule:** Contractions like *Ko in* are invalid developmental forms and must be flagged as schema errors.

### DERIVATIONAL
Applies to affixation processes that shift syntactic categories or structurally alter semantic values.

*   **Prefixation:** Nominalizers like *na-* (turns verbs to nouns).
    *   *Example:* *sep* (to work, `VERB`) $\rightarrow$ *nasep* (job/work, `NOUN`).
*   **Suffixation:** Adverbializers or collective markers.
    *   *Example:* *manlang* (quick, `ADJ`) + *-takin* $\rightarrow$ *manlangtakin* (quickly, `ADV`).

### COMPOUND
Zomi relies heavily on compounding for lexical expansion. Compounding **must not** be restricted to nouns.

*   **Noun Compounds (`NOUN`):** *inn* (house) + *tual* (ground) $\rightarrow$ *inntual* (courtyard).
*   **Serial Verbs / Complex Predicates (`VERB`):** Multi-root structures forming a unified semantic action.
    *   *Example:* *mu* (to see) + *khia* (to emerge) $\rightarrow$ *mukhia* (to discover/find).
*   **Noun-Adjective Compounds (`ADJ`):** *lung* (heart/mind) + *khauh* (stiff/strong) $\rightarrow$ *lungkhauh* (stubborn/resolute).

### NONE
Closed-class grammatical words that never modify their phonological, tonal, or structural baseline.

*   **Particles (`PART`):** Standard discourse markers such as *maw* or *ve*.
    > ⚠️ **Orthography Constraint:** Combined dialectal artifacts or invalid contractions like *mawe* must be rejected by the validation pipeline. Only *maw* or *ve* are permitted independently.

---

## 3. JSON Schema Implementation

This specification is programmatically enforced using a shared reference schema (`definitions.json`). Individual entry validation pipelines (e.g., `verb_entry.json`) reference this block to guarantee cross-dataset consistency.

```json
{
  "$schema": "[https://json-schema.org/draft/2020-12/schema](https://json-schema.org/draft/2020-12/schema)",
  "$id": "[https://zomi-nlp.org/schemas/definitions.json](https://zomi-nlp.org/schemas/definitions.json)",
  "title": "Zomi Morph Type Constraints",
  "$defs": {
    "zomi_morph_type_validation": {
      "type": "object",
      "properties": {
        "upos": { "type": "string" },
        "morph_type": { "type": "string" }
      },
      "required": ["upos", "morph_type"],
      "allOf": [
        {
          "if": { "properties": { "morph_type": { "const": "INFLECTIONAL" } } },
          "then": { "properties": { "upos": { "enum": ["NOUN", "VERB", "ADJ", "PRON", "DET", "NUM", "AUX", "ADV"] } } }
        },
        {
          "if": { "properties": { "morph_type": { "const": "DERIVATIONAL" } } },
          "then": { "properties": { "upos": { "enum": ["NOUN", "VERB", "ADJ", "ADV", "NUM"] } } }
        },
        {
          "if": { "properties": { "morph_type": { "const": "COMPOUND" } } },
          "then": { "properties": { "upos": { "enum": ["NOUN", "VERB", "ADJ", "ADV"] } } }
        },
        {
          "if": { "properties": { "morph_type": { "const": "NONE" } } },
          "then": { "properties": { "upos": { "enum": ["ADP", "CCONJ", "SCONJ", "PART", "INTJ", "PUNCT", "SYM"] } } }
        },
        {
          "if": { "properties": { "morph_type": { "const": "NON_LINGUISTIC" } } },
          "then": { "properties": { "upos": { "enum": ["SYM", "X"] } } }
        }
      ]
    }
  }
}
```
