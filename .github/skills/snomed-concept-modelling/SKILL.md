# SNOMED CT concept modelling

Use this skill when the term-mapping workflow returns `NO_MAP` or when a user asks for a structured SNOMED CT concept proposal.

## Purpose and boundary

Produce two clearly separated representations:

- A post-coordinated SNOMED CT expression for local evaluation, when the meaning can be represented with the available terminology edition and syntax.
- A review-ready proposal for a new concept to submit through the responsible National Release Center or another authorised SNOMED CT authoring process.

A local agent must not assign a new SCTID. A proposal is not an approved SNOMED CT concept, and a post-coordinated expression is not a new pre-coordinated concept.

## Required inputs

Ask for missing information before modelling:

- The unresolved source term and its clinical definition.
- Synonyms, language, intended users, and use case.
- Clinical context, including finding versus procedure, body site, morphology, laterality, severity, temporality, and method where applicable.
- Evidence or references supporting the meaning.
- The intended SNOMED CT edition and release.
- The responsible organisation, extension namespace or authoring service, if a local extension is intended.

Do not infer a clinical definition from a short label alone. Ask for clarification when the term is ambiguous.

## Workflow

1. Review the mapping skill's candidate searches and confirm that `NO_MAP` is justified for the supplied edition and release.
2. Identify the closest valid hierarchy and proximal primitive supertype using the local `sct` MCP tools. Verify active status and release.
3. Inspect available relationships, attributes, value hierarchies, and constraints. Use ECL or equivalent hierarchy queries where available. Do not assume that an attribute is valid merely because it is common in another hierarchy.
4. Separate stated meaning from modelling assumptions. List unresolved clinical or editorial questions before writing the final expression.
5. Construct a post-coordinated expression in SNOMED Compositional Grammar using existing SCTIDs and terms. Keep the expression parsable and mark whether it is stated or inferred where that distinction matters.
6. Validate the expression with the available `sct` tooling, and report validation limitations. Never claim that an expression is valid when it was not checked.
7. Prepare a new-concept proposal containing an FSN, preferred terms, synonyms, hierarchy, defining characteristics, and clinical rationale. Use semantic tags appropriate to the proposed meaning, but flag them for authoring review.
8. Explain what requires review by a clinician, terminology author, extension owner, or National Release Center.

Use the exact MCP tool names and parameters exposed by the connected server. If MRCM validation, expression parsing, or a required relationship lookup is unavailable, state that explicitly and do not fabricate a result.

## Output

### Track A: post-coordinated expression

Provide:

- Human-readable meaning.
- SNOMED Compositional Grammar expression, with existing SCTIDs and FSNs.
- Edition and release.
- Stated versus inferred attributes.
- Validation command or MCP operation used and its result.
- Known limitations and clinical review questions.

Use a placeholder such as `<existing SCTID required>` only when a real identifier has not been retrieved. Never invent an SCTID for an example.

### Track B: authoring proposal

Provide a structured proposal with:

- Proposal status: `Draft - not an approved SNOMED CT concept`.
- FSN in English and, when required, the local language, including the semantic tag.
- Preferred term and acceptable synonyms.
- Proposed `Is a` parents.
- Defining characteristics grouped by attribute and value.
- Clinical definition and scope.
- Rationale explaining why existing concepts and postcoordination do not meet the use case.
- Evidence and references.
- Impact, duplication, and ambiguity risks.
- Questions for authoring and clinical review.
- Responsible extension or submission route.

Do not include a made-up SCTID. The responsible authoring process assigns identifiers after review and acceptance.

## Guardrails

- Do not mint local identifiers and present them as SNOMED CT identifiers.
- Do not present a draft as endorsed, published, or clinically safe.
- Do not add unsupported relationships to make an expression look complete.
- Do not bypass the applicable MRCM, authoring, licensing, or National Release Center process.
- Do not expose proprietary clinical source data outside the approved environment.
- Keep postcoordination and precoordination clearly labelled in every output.

## Handoff back to mapping

When a proposal is accepted or a post-coordinated expression is selected, return the source term, chosen representation, release, review decision, and responsible reviewer. The mapping report should still retain the original `NO_MAP` decision and link to the reviewed modelling outcome.
