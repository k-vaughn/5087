### Recommended Annotation Properties for OWL Ontologies

Based on widely accepted best practices from sources like FAIR ontology guidelines, OBO Foundry (biomedical ontologies), W3C recommendations, Protégé defaults, and case studies (e.g., CASE ontology), the most effective approach is to prioritize properties from a small set of standard vocabularies: RDFS (for basic comments and labels), OWL (for versioning and deprecation), DCTERMS (for metadata like sources, licenses, and dates), and SKOS (for detailed definitions, notes, and examples). This minimizes imports to just four namespaces (RDFS and OWL are typically already imported in any OWL ontology, so effectively adding only DCTERMS and SKOS).

These vocabularies are broadly adopted across domains (e.g., Dublin Core in Protégé defaults, SKOS in semantic web vocabularies, OWL for core ontology mechanics). Using them avoids niche ones like IAO (OBO-specific) or VANN (optional for namespaces). For non-standard items like security attributes, a custom property is suggested, as no universal standard exists.

Here's a mapping of your requirements to recommended properties. Each includes the property, namespace, rationale (why it's widely accepted and fits), and usage notes. Properties support multiplicity where needed (e.g., via repeated assertions).

| Requirement | Recommended Property | Namespace | Rationale and Usage Notes |
|-------------|----------------------|-----------|---------------------------|
| Definition | `skos:definition` | http://www.w3.org/2004/02/skos/core# | More precise than `rdfs:comment` for formal definitions; widely used in SKOS-based vocabularies and ontologies like CASE. Use one per language if multilingual. Fall back to `rdfs:comment` (http://www.w3.org/2000/01/rdf-schema#) if minimizing SKOS import. |
| Source (may be multiple) | `dcterms:source` | http://purl.org/dc/terms/ | Standard for citing origins or references; repeatable for multiples. Common in FAIR guidelines and Dublin Core for provenance. Can point to URIs or literals. |
| Notes (may be multiple) | `skos:note` | http://www.w3.org/2004/02/skos/core# | General-purpose for annotations; repeatable. Subproperties like `skos:editorialNote` or `skos:historyNote` for specifics if needed. Widely adopted for flexible documentation in semantic web practices. |
| Example (may be multiple) | `skos:example` | http://www.w3.org/2004/02/skos/core# | Explicitly for illustrative examples; repeatable. Recommended in SKOS and FAIR practices for reusability. Can be literals or URIs to resources. |
| License (of ontology file only) | `dcterms:license` | http://purl.org/dc/terms/ | Standard for legal usage terms; points to a license URI (e.g., CC-BY). Used in ontology headers per FAIR and W3C best practices. Apply to the ontology IRI. |
| Date (of ontology file only) | `dcterms:created` | http://purl.org/dc/terms/ | For creation date; xsd:date datatype. Widely used in Dublin Core and Protégé. Alternative: `dcterms:date` for general dates. Apply to ontology IRI. |
| Modified (date and description) | `dcterms:modified` (for date) + `skos:changeNote` (for description) | http://purl.org/dc/terms/ + http://www.w3.org/2004/02/skos/core# | `dcterms:modified` is standard for last update (xsd:date); pair with repeatable `skos:changeNote` for descriptions. Aligns with FAIR versioning and SKOS for history. Use `owl:versionInfo` (http://www.w3.org/2002/07/owl#) for simple version strings if avoiding SKOS. |
| Identifier for another item that this item replaces | `dcterms:replaces` | http://purl.org/dc/terms/ | Points to the replaced item's URI. Standard in Dublin Core for succession; repeatable if needed. Common in ontology evolution practices. |
| Identifier for another item that replaces this item | `dcterms:isReplacedBy` | http://purl.org/dc/terms/ | Points to the replacing item's URI. Inverse of above; widely used for deprecation chains in FAIR and W3C guidelines. |
| Whether the item is current, deprecated, or obsolete | `owl:deprecated` | http://www.w3.org/2002/07/owl# | Boolean (true for deprecated/obsolete); core OWL feature for classes/properties. For finer status (e.g., "current" vs. "obsolete"), add `skos:note` or use `sw:term_status` (http://www.w3.org/2003/06/sw-vocab-status/ns#) with values like "stable" or "archaic"—but the latter adds another import, so prefer OWL + SKOS note for minimalism. |
| Security attributes (e.g., whether the item is considered PII) | Custom property, e.g., `:hasSecurityAttribute` (or `dcterms:rights` for general rights) | Your ontology's namespace (or http://purl.org/dc/terms/) | No universal standard; custom is common for domain-specific needs like PII flags. Use `dcterms:rights` for rights statements if it fits, as it's widely accepted in Dublin Core. Value could be a literal (e.g., "PII: true") or link to a security ontology if needed. |
|Abstract|`protoge:abstract`|||

### Minimizing Imports
- **Core (0 additional imports)**: RDFS and OWL cover basics (e.g., definitions via `rdfs:comment`, deprecation via `owl:deprecated`).
- **Recommended (2 additional imports)**: Add DCTERMS (for metadata/provenance) and SKOS (for detailed annotations). These are imported via simple `owl:imports` statements in your TTL file.
- **Why minimal?** Avoids extras like IAO (OBO-specific), ADMS (asset status), or PROV (full provenance). If your ontology is simple, skip SKOS and use `rdfs:comment` for definitions/notes/examples.
- **Example Import Statements in TTL**:
  ```
  @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
  @prefix owl: <http://www.w3.org/2002/07/owl#> .
  @prefix dcterms: <http://purl.org/dc/terms/> .
  @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
  
  <your-ontology-iri> owl:imports dcterms:, skos: .
  ```

This setup ensures compatibility with tools like Protégé, supports FAIR principles, and is reusable across domains without bloat. For PII/security, define a custom property in your ontology to avoid further imports.<grok:render card_id="339590" card_type="citation_card" type="render_inline_citation">
<argument name="citation_id">45</argument>
</grok:render><grok:render card_id="bbd75c" card_type="citation_card" type="render_inline_citation">
<argument name="citation_id">42</argument>
</grok:render><grok:render card_id="c4fd2d" card_type="citation_card" type="render_inline_citation">
<argument name="citation_id">43</argument>
</grok:render><grok:render card_id="c68ea3" card_type="citation_card" type="render_inline_citation">
<argument name="citation_id">44</argument>
</grok:render>