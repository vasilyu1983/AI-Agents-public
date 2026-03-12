# OS Agent Capabilities — Best Practices

*Purpose: Provide operational patterns for perception, grounding, planning, UI interaction, and verification for OS-level agents (desktop, web, mobile).*

---

# 1. OS Agent Architecture (Operational)

### Core Loop

```
OBSERVE(window_state)
GROUND(target_element)
ACT(click/type/scroll/shortcut)
VERIFY(state_changed)
```

**Checklist**

- [ ] Loop runs per step, not globally.  
- [ ] Each observation updates actionable state.  
- [ ] Grounding completes before action.  
- [ ] Verification validates intended state change.  

---

# 2. Perception (Observation)

### Pattern: Structured Screen Capture

```
capture_screenshot()
extract_ui_tree()
extract_text_blocks()
extract_positions()
normalize_state()
```

**Checklist**

- [ ] Capture full viewport.  
- [ ] Include bounding boxes with coordinates.  
- [ ] Include role/type/label for each element.  
- [ ] Include OCR when text not available in UI tree.  

**Anti-Patterns**

- AVOID: Using raw images without structure.  
- AVOID: Guessing element positions.  

---

# 3. Grounding (Element Identification)

### Pattern: Deterministic Element Selection

```
find_element(criteria)
rank_candidates()
select_best_match()
verify_element_exists()
```

**Matching Criteria**

- role (button, field, link)  
- label/text  
- aria attributes  
- position constraints  
- icon description  

**Checklist**

- [ ] At least two criteria match.  
- [ ] Reject ambiguous matches (>1 candidate).  
- [ ] Validate element visible + enabled.  

**Decision Tree**

```
Is exact-text match found?
→ Yes → use it
→ No → fallback to approximate match
If >1 match → disambiguate or ask user
```

---

# 4. UI Navigation

### Pattern: Intent-Based Navigation

```
map_intent_to_target()
navigate_to_section()
confirm_visibility()
```

**Checklist**

- [ ] Identify nearest navigable parent (tab, menu, section).  
- [ ] Avoid unnecessary page reloads.  
- [ ] Scroll only when item is off-screen.  

**Anti-Patterns**

- AVOID: Blind scrolling.  
- AVOID: Navigating without checking for location change.  

---

# 5. Actions (Execution)

## 5.1 Click Actions

```
hover(optional)
click(element.bounding_box.center)
```

**Checklist**

- [ ] Click center point (safe zone).  
- [ ] Confirm element not obstructed.  
- [ ] Add small delay (100–250ms) if needed.  

**Anti-Patterns**

- AVOID: Clicking coordinate literals without grounding.  
- AVOID: Clicking non-visible elements.  

---

## 5.2 Typing Actions

```
focus(element)
type(text)
```

**Checklist**

- [ ] Clear existing text if required.  
- [ ] Type at controlled speed (if OS needs).  
- [ ] Submit only after verification.  

---

## 5.3 Scroll Actions

```
if element not visible:
    scroll(direction)
    re-observe()
```

**Checklist**

- [ ] Scroll small increments.  
- [ ] Re-run perception each scroll.  

---

## 5.4 Shortcut Actions (Keyboard Commands)

```
send_shortcut(["ctrl","h"])
verify_ui_changed()
```

**Checklist**

- [ ] Confirm OS-specific shortcut validity.  
- [ ] Avoid destructive shortcuts.  
- [ ] Rerun perception to validate state.  

---

# 6. Verification (Post-Action Check)

### Pattern: State Change Verification

```
expected_state = define_preconditions()
post_state = observe()
compare(expected_state, post_state)
```

**Checklist**

- [ ] Confirm element clicked triggered action.  
- [ ] Confirm field text updated.  
- [ ] Confirm navigation completed.  
- [ ] Confirm UI tree changed as expected.  

**Decision Tree**

```
Did expected element appear?
→ Yes → success
→ No → retry once
→ Still no → revise plan
```

**Anti-Patterns**

- AVOID: Proceeding without verifying success.  
- AVOID: Assuming action worked based on timing alone.  

---

# 7. Error & Recovery Patterns

### Pattern: Recoverable Error Handling

```
if ui_state_unexpected:
    re-observe
    try_different_path
    escalate
```

**Recoverable Cases**

- Missing element  
- Partial load  
- Scroll mismatch  
- Timing delay  

**Fatal Cases**

- Permission denied  
- System alert blocking UI  
- Full navigation failure  

---

# 8. Page/Screen State Normalization

### Pattern: Normalize UI State

```
collapse_popups()
close_modals()
remove_overlays()
focus_primary_app()
```

**Checklist**

- [ ] Clear popovers before grounding.  
- [ ] Close notifications blocking clickable elements.  
- [ ] Ensure main window is active.  

---

# 9. Multi-Step OS Tasks

### Pattern: Stepwise OS Automation

```
for step in plan:
    observe
    ground
    act
    verify
```

**Checklist**

- [ ] Each step has defined expected outcome.  
- [ ] Plan adjusts after each observation.  
- [ ] No long speculative chains.  

---

# 10. Accessibility-First Grounding

### Use When Available

- aria-label  
- aria-role  
- accessibility names  
- tab order  
- keyboard navigability  

**Why It Matters (Operational-Only)**

- determinism  
- easier matching  
- avoids coordinate guessing  

---

# 11. Window & App Control

### Pattern: Window Management

```
ensure_app_in_foreground()
verify_window_title()
maximize_if_needed()
```

**Checklist**

- [ ] Correct app selected.  
- [ ] Window not hidden/minimized.  
- [ ] Focus restored after each action.  

---

# 12. Browser-Specific Patterns

### Pattern: DOM-Grounded Selection

```
locate_node(css/xpath)
verify_visible()
scroll_into_view()
click()
```

**Checklist**

- [ ] Prefer CSS selectors over XPath.  
- [ ] Reject hidden nodes.  
- [ ] Validate element index if duplicates exist.  

---

# 13. Mobile-Specific Patterns

### Pattern: Mobile Interaction

```
tap(element.center)
swipe(start → end)
wait_for_animation()
```

**Checklist**

- [ ] Use accessibility ID when available.  
- [ ] Avoid pixel-based coordinates; use bounding boxes.  
- [ ] Re-observe after screen transitions.  

---

# 14. OS Agent Anti-Patterns (Master List)

- AVOID: Blind clicking by coordinates.  
- AVOID: Acting without grounding.  
- AVOID: Not re-observing after UI change.  
- AVOID: Ignoring obstructions (modals, popovers).  
- AVOID: Hard-coding UI paths.  
- AVOID: Performing multi-step actions without intermediate verification.  
- AVOID: Failing to validate element visibility/enabled state.  
- AVOID: Scrolling arbitrarily without checking viewport.  

---

# 15. Quick Reference Tables

### Element Types Table

| Type | Recognition Feature |
|------|----------------------|
| Button | label, role, icon |
| Input | placeholder, aria-role |
| Link | href/text |
| Modal | overlay + center element |
| Menu | vertical list structure |

### Common OS Actions

| Action | When to Use |
|--------|--------------|
| click | select element |
| type | enter data |
| scroll | move viewport |
| shortcut | open dialogs, commands |
| hover | reveal menus |

### Verification Points

| Step | Required Check |
|------|----------------|
| After click | UI changed |
| After type | Text updated |
| After scroll | Target visible |
| After navigation | Correct page/section |

---

# End of File
