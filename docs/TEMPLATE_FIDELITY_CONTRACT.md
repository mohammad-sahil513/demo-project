# Template Fidelity Contract

## Purpose
Define strict enterprise fidelity rules for custom templates.

## Rule
Only placeholder values may change in final output.

## Must Preserve
- Header and footer structure/content.
- Logos and embedded images/media relationships.
- Page setup, section breaks, numbering, watermark/background.
- Styles/layout outside placeholder ranges.

## Allowed Changes
- Text, rich text, list, table, and image content at declared placeholders only.

## Strict Mode Blocking
Output must be blocked when:
- Required placeholder unresolved.
- Header/footer integrity fails.
- Media relationship integrity fails.
- Contract validation is invalid.

## LLM Boundary
- LLM allowed: generate placeholder payload content.
- LLM prohibited: deciding output structure mutations in strict mode.
