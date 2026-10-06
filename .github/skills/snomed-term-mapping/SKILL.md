# SNOMED CT term mapping

Use this skill to map a local proprietary term list to SNOMED CT with the available `sct` MCP tools.

## Purpose

Produce a reviewable mapping, not an unqualified automatic conversion. Preserve the source term exactly, show the SNOMED CT concept selected, and make uncertainty visible.

## Required inputs

Ask for these inputs when they are not supplied:

- The source list as CSV, JSON, or pasted rows.
- The source language and any local codes, descriptions, synonyms, or context.
- The intended SNOMED CT edition and release, including whether Swedish descriptions are required.
- An optional domain restriction, such as Clinical finding or Procedure, and any relevant ECL hierarchy.
- The desired output format: Markdown table, CSV, or FHIR ConceptMap JSON.

Do not send proprietary data to an external service unless the user has explicitly authorised it. Prefer the local `sct` MCP server and local files.

## Workflow

For each source row:

1. Preserve the original source code and term. Do not silently normalise, translate, or discard qualifiers.
2. Search the local `sct` database lexically for exact terms, descriptions, and known synonyms.
3. Use semantic or embedding search when it is available and appropriate. Treat semantic matches as candidates, not proof of equivalence.
4. Inspect candidate details, active status, FSN, preferred terms, synonyms, language, module, and release. Record the edition and release used.
5. Check the candidate's hierarchy and defining relationships. Use ECL or hierarchy tools to verify a supplied domain restriction. A text match alone is insufficient.
6. Compare the full meaning, including body site, morphology, laterality, severity, finding versus procedure, temporal context, and other qualifiers.
7. Assign one mapping relationship:
   - `EQUIVALENT`: the source and target have the same clinical meaning.
   - `SOURCE_IS_NARROWER_THAN_TARGET`: the target is broader and loses source specificity.
   - `SOURCE_IS_BROADER_THAN_TARGET`: the target is narrower and would add unsupported specificity.
   - `NO_MAP`: no acceptable target was found.
8. Assign confidence (`High`, `Medium`, or `Low`) and explain the decision in plain language.
9. Put every `NO_MAP`, ambiguous match, inactive concept, and unsupported semantic inference into a review queue. Do not force a code.

Use the exact MCP tool names and parameters exposed by the connected server. If a requested search or relationship cannot be verified with the available tools, say so and lower confidence rather than inventing a result.

## Output

Return a row for every source item with at least:

| Source code | Source term | SNOMED CT ID | FSN | Preferred term | Relationship | Confidence | Rationale | Review status |
|---|---|---:|---|---|---|---|---|---|

For `NO_MAP`, leave the SNOMED CT fields empty and set `Review status` to `Needs modelling`. For a FHIR ConceptMap, preserve the same information in mappings and extensions or an accompanying review report; do not hide rationale and confidence in prose only.

Finish with a short summary of counts by relationship and a list of unresolved rows. Include the SNOMED CT edition, release date, language reference set, search methods used, and any assumptions.

## Guardrails

- Never create or guess a SNOMED CT identifier.
- Never treat a lexical or semantic similarity score as clinical equivalence.
- Never map across incompatible hierarchies merely because the words are similar.
- Never use an inactive concept without flagging it and checking the edition's replacement guidance.
- Do not claim that a mapping is clinically approved. Require terminology or clinical review before production use.
- Keep source data and generated mappings local unless explicit permission says otherwise.

## Handoff to modelling

Export unresolved rows with the original source context, failed search terms, candidate concepts considered, and the reason for `NO_MAP`. These rows are the input to the `snomed-concept-modelling` skill.
