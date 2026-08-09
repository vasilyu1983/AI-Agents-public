# DOCX Template Authoring Checklist

Use this when handing a Word-authored template to engineering or operations for automation.

## Template Structure

- [ ] Template file type is correct (`.docx` or `.dotx`, not `.doc`)
- [ ] Macro-enabled files (`.docm` / `.dotm`) are avoided unless explicitly required
- [ ] Heading styles use Word built-in styles
- [ ] Lists use list styles, not typed bullets/numbers
- [ ] Tables are for data, not page layout
- [ ] Header/footer usage is intentional and documented

## Placeholder Discipline

- [ ] Every placeholder is named consistently
- [ ] Placeholder casing and separators are consistent (`snake_case` recommended)
- [ ] Required vs optional placeholders are documented
- [ ] Repeated content uses a documented loop pattern
- [ ] Placeholder examples do not leak real customer or legal data

## Visual Discipline

- [ ] Fonts are deliberate and portable
- [ ] Complex numbering is avoided unless tested outside Word
- [ ] Floating images are avoided unless strictly necessary
- [ ] Charts/tables still make sense when exported to PDF
- [ ] Manual formatting is minimized in favor of styles

## Accessibility Hygiene

- [ ] Heading hierarchy is sequential
- [ ] Informative images have alt text
- [ ] Tables have a clear header row
- [ ] Hyperlinks are descriptive
- [ ] Document language is set at the template level where possible

## Automation Handoff

- [ ] Expected input schema exists (JSON/CSV/API fields)
- [ ] Sample context data exists
- [ ] Output filename rules are documented
- [ ] Review/comment workflow is documented
- [ ] Quality gate expectations are documented

## Release Checks

- [ ] Opens correctly in Word
- [ ] Smoke-tested in one non-Word viewer if distribution requires it
- [ ] PDF export path is defined if the document is externally distributed
- [ ] Versioning and owner are documented
