# Markdown Style Guide

Comprehensive guide to writing clear, consistent, and accessible Markdown documentation.

## Table of Contents

- [Basic Syntax](#basic-syntax)
- [Extended Syntax](#extended-syntax)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Accessibility](#accessibility)
- [Tools and Linters](#tools-and-linters)

---

## Basic Syntax

### Headings

Use ATX-style headings (# symbols) with a space after the #.

**Good:**
```markdown
# Heading 1
## Heading 2
### Heading 3
```

**Bad:**
```markdown
#Heading 1          # Missing space
##Heading 2         # Missing space

Heading 1           # Setext-style (inconsistent)
=========
```

**Rules:**
- Only one H1 per document
- Don't skip heading levels (H1 → H3)
- Use sentence case, not title case
- Don't put punctuation at the end

### Paragraphs

Separate paragraphs with a blank line.

**Good:**
```markdown
This is the first paragraph.

This is the second paragraph.
```

**Bad:**
```markdown
This is the first paragraph.
This is the second paragraph.
```

### Line Breaks

Use two trailing spaces or `<br>` for hard line breaks (avoid if possible).

**Soft wrap (preferred):**
```markdown
This is a long paragraph that will wrap automatically based on the viewer's window size.
```

**Hard break (only when needed):**
```markdown
Line 1
Line 2
```

### Emphasis

**Bold:**
```markdown
**bold text**
__also bold__
```

**Italic:**
```markdown
*italic text*
_also italic_
```

**Bold and italic:**
```markdown
***bold and italic***
___also bold and italic___
```

**Strikethrough (GitHub Flavored Markdown):**
```markdown
~~strikethrough~~
```

**Recommendation:** Use `**` for bold and `*` for italic (more widely supported).

### Lists

#### Unordered Lists

Use `-`, `*`, or `+` (be consistent).

**Good:**
```markdown
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3
```

**Bad:**
```markdown
- Item 1
* Item 2          # Mixed markers
  - Nested item
 - Nested item    # Incorrect indentation
```

**Rules:**
- Use 2 or 4 spaces for nesting (be consistent)
- Add blank lines before and after lists
- Use `-` as the default marker

#### Ordered Lists

Use numbers followed by a period.

**Good:**
```markdown
1. First item
2. Second item
3. Third item
```

**Also acceptable (lazy numbering):**
```markdown
1. First item
1. Second item
1. Third item
```

**Bad:**
```markdown
1) First item     # Wrong delimiter
2) Second item
```

#### Task Lists (GitHub Flavored Markdown)

```markdown
- [ ] Unchecked task
- [x] Checked task
```

### Links

#### Inline Links

```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Hover text")
```

#### Reference Links

```markdown
This is a [reference link][ref].

[ref]: https://example.com "Title"
```

#### Automatic Links

```markdown
<https://example.com>
<email@example.com>
```

**Best practices:**
- Use descriptive link text (not "click here")
- Add titles for additional context
- Use reference links for repeated URLs

### Images

```markdown
![Alt text](image.png)
![Alt text](image.png "Image title")
```

**With reference:**
```markdown
![Alt text][logo]

[logo]: /path/to/logo.png "Logo title"
```

**Best practices:**
- Always include alt text for accessibility
- Use descriptive file names
- Optimize image sizes

### Code

#### Inline Code

```markdown
Use `backticks` for inline code.
```

#### Code Blocks

**Fenced code blocks (preferred):**

````markdown
```javascript
function hello() {
  console.log('Hello, world!');
}
```
````

**With syntax highlighting:**

````markdown
```python
def hello():
    print("Hello, world!")
```
````

**Indented code blocks (avoid):**
```markdown
    # Less clear
    function hello() {
      console.log('Hello');
    }
```

**Best practices:**
- Always specify language for syntax highlighting
- Keep code examples concise and relevant
- Test code examples before publishing

### Blockquotes

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
>
> > Nested blockquote
```

### Horizontal Rules

```markdown
---

***

___
```

**Recommendation:** Use `---` for consistency.

---

## Extended Syntax

### Tables

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

**With alignment:**

```markdown
| Left align | Center align | Right align |
|:-----------|:------------:|------------:|
| Left       | Center       | Right       |
```

**Best practices:**
- Align pipes for readability
- Keep tables simple (use HTML for complex tables)
- Add blank lines before and after tables

### Footnotes

```markdown
Here's a sentence with a footnote[^1].

[^1]: This is the footnote text.
```

### Definition Lists

```markdown
Term 1
: Definition 1

Term 2
: Definition 2a
: Definition 2b
```

### Emoji (GitHub Flavored Markdown)

```markdown
:smile: :heart: :thumbsup:
```

**Recommendation:** Use sparingly in technical documentation.

### Admonitions (Some renderers)

```markdown
!!! note
    This is a note.

!!! warning
    This is a warning.
```

---

## Best Practices

### 1. Use Consistent Formatting

**Bad:**
```markdown
# Title
some text

##Another Heading
More text without spacing.

- list item
* different marker
```

**Good:**
```markdown
# Title

Some text with proper spacing.

## Another Heading

More text with consistent formatting.

- List item
- Same marker throughout
```

### 2. Keep Line Length Reasonable

**Recommendation:** 80-120 characters per line for readability.

**Good:**
```markdown
This is a reasonably short line that wraps naturally and is easy to read
in any editor or viewer.
```

**Bad:**
```markdown
This is an extremely long line that goes on and on and on and makes it difficult to read in narrow viewports or when viewing diffs and really should be broken up into smaller chunks for better readability.
```

### 3. Use Descriptive Link Text

**Bad:**
```markdown
Click [here](https://example.com) for more information.
```

**Good:**
```markdown
See the [installation guide](https://example.com/install) for setup instructions.
```

### 4. Add Blank Lines for Readability

**Bad:**
```markdown
# Heading
Text immediately after heading.
## Another Heading
More text without spacing.
- List item
- Another item
```

**Good:**
```markdown
# Heading

Text with proper spacing.

## Another Heading

More text with good visual separation.

- List item
- Another item
```

### 5. Use Semantic Headings

**Bad:**
```markdown
# Title
### Skipped H2
## Wrong Order
```

**Good:**
```markdown
# Title
## Section 1
### Subsection 1.1
## Section 2
```

### 6. Include Table of Contents for Long Documents

```markdown
## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
  - [Subsection 2.1](#subsection-21)
```

### 7. Use Code Blocks with Syntax Highlighting

**Bad:**
````markdown
```
function hello() {
  console.log('Hello');
}
```
````

**Good:**
````markdown
```javascript
function hello() {
  console.log('Hello');
}
```
````

### 8. Test Links Before Publishing

Use tools like `markdown-link-check`:

```bash
npx markdown-link-check README.md
```

---

## Common Pitfalls

### 1. Mixing Markdown Flavors

Different renderers support different features. Stick to CommonMark for maximum compatibility.

**Problematic:**
```markdown
==highlight==        # Not widely supported
```

**Safe alternative:**
```markdown
**highlight**        # Works everywhere
```

### 2. Incorrect List Indentation

**Wrong:**
```markdown
- Item 1
 - Nested item     # Only 1 space
   - Deep nested   # 3 spaces
```

**Correct:**
```markdown
- Item 1
  - Nested item   # 2 spaces
    - Deep nested # 4 spaces
```

### 3. Missing Alt Text for Images

**Bad:**
```markdown
![](image.png)
```

**Good:**
```markdown
![Descriptive alt text](image.png)
```

### 4. Using HTML When Markdown Would Work

**Bad:**
```markdown
<strong>Bold text</strong>
<em>Italic text</em>
```

**Good:**
```markdown
**Bold text**
*Italic text*
```

**When to use HTML:** Complex tables, specific styling needs, embedding media.

---

## Accessibility

### 1. Use Descriptive Alt Text

```markdown
# Bad
![image](logo.png)

# Good
![Company logo showing a blue mountain](logo.png)
```

### 2. Use Semantic Headings

- Only one H1 per document
- Don't skip levels (H1 → H3)
- Use headings for structure, not styling

### 3. Descriptive Link Text

```markdown
# Bad
[Click here](https://example.com)

# Good
[Read the installation guide](https://example.com/install)
```

### 4. Provide Text Alternatives for Diagrams

```markdown
![Architecture diagram](architecture.png)

**Text description:** The system consists of three layers: presentation (web UI),
application (API server), and data (PostgreSQL database).
```

### 5. Use Tables Appropriately

- Add header row
- Keep tables simple
- Provide alternative formats for complex data

---

## Tools and Linters

### markdownlint

```bash
# Install
npm install -g markdownlint-cli

# Lint files
markdownlint README.md

# Fix automatically
markdownlint --fix README.md
```

**Configuration (.markdownlint.json):**
```json
{
  "default": true,
  "MD013": false,
  "MD033": false
}
```

### markdown-link-check

```bash
# Install
npm install -g markdown-link-check

# Check links
markdown-link-check README.md
```

### Vale

```bash
# Install
brew install vale

# Lint prose
vale README.md
```

### Prettier

```bash
# Install
npm install -g prettier

# Format Markdown
prettier --write "**/*.md"
```

---

## Quick Reference

### Headers
```markdown
# H1
## H2
### H3
```

### Emphasis
```markdown
**bold**
*italic*
***bold italic***
```

### Lists
```markdown
- Unordered item
- Another item

1. Ordered item
2. Another item
```

### Links and Images
```markdown
[Link text](https://example.com)
![Alt text](image.png)
```

### Code
````markdown
`inline code`

```language
code block
```
````

### Blockquotes and Rules
```markdown
> Blockquote

---
```

### Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

---

## Resources

- [CommonMark Specification](https://commonmark.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Markdown Guide](https://www.markdownguide.org/)
- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [Google Developer Documentation Style Guide](https://developers.google.com/style/markdown)
