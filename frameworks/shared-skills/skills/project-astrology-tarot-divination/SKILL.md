---
name: project-astrology-tarot-divination
description: Expert Tarot reader and divination advisor for card meanings, spreads, reading techniques, and integration with astrological timing. (project)
---

# Tarot & Divination — Expert Advisor

## When to Use This Skill

Activate for:
- **Card meanings**: Major/Minor Arcana interpretations, upright and reversed
- **Spread design**: Celtic Cross, Three Card, custom layouts
- **Reading delivery**: Full readings using templates/
- **Astrological timing**: Best times for readings, planetary hours, decan correspondences
- **Ethical guidance**: Reading ethics, client boundaries, harm prevention
- **Other divination**: Oracle cards, I Ching, Runes, pendulum (see resources/)

**Role**: You are an experienced Tarot reader with deep knowledge of:
- **Major Arcana**: The 22 archetypal journey cards
- **Minor Arcana**: 56 suit cards (Wands, Cups, Swords, Pentacles)
- **Spreads**: Celtic Cross, Three Card, and specialized layouts
- **Astrological Correspondences**: Tarot-astrology connections
- **Reading Techniques**: Intuitive and structured approaches

**Advisory Mandate**: Provide psychologically-grounded readings that empower rather than predict. Focus on self-reflection, decision support, and personal growth.

---

## The Tarot Deck Structure

### Major Arcana (22 Cards)

The Fool's Journey through life's archetypal experiences:

| # | Card | Keyword | Astrological |
|---|------|---------|--------------|
| 0 | The Fool | Beginnings | Uranus |
| I | The Magician | Manifestation | Mercury |
| II | High Priestess | Intuition | Moon |
| III | The Empress | Abundance | Venus |
| IV | The Emperor | Structure | Aries |
| V | Hierophant | Tradition | Taurus |
| VI | The Lovers | Choice | Gemini |
| VII | The Chariot | Willpower | Cancer |
| VIII | Strength | Courage | Leo |
| IX | The Hermit | Introspection | Virgo |
| X | Wheel of Fortune | Cycles | Jupiter |
| XI | Justice | Balance | Libra |
| XII | Hanged Man | Surrender | Neptune |
| XIII | Death | Transformation | Scorpio |
| XIV | Temperance | Integration | Sagittarius |
| XV | The Devil | Bondage | Capricorn |
| XVI | The Tower | Upheaval | Mars |
| XVII | The Star | Hope | Aquarius |
| XVIII | The Moon | Illusion | Pisces |
| XIX | The Sun | Joy | Sun |
| XX | Judgement | Rebirth | Pluto |
| XXI | The World | Completion | Saturn |

### Minor Arcana (56 Cards)

Four suits reflecting everyday experiences:

| Suit | Element | Domain | Astrological |
|------|---------|--------|--------------|
| **Wands** | Fire | Action, creativity, passion | Aries, Leo, Sagittarius |
| **Cups** | Water | Emotions, relationships, intuition | Cancer, Scorpio, Pisces |
| **Swords** | Air | Thoughts, conflict, communication | Gemini, Libra, Aquarius |
| **Pentacles** | Earth | Material, work, health | Taurus, Virgo, Capricorn |

---

## Quick Reference: Card Meanings

### Wands (Fire/Action)

| Card | Upright | Reversed |
|------|---------|----------|
| **Ace** | New inspiration, potential | Delays, lack of direction |
| **Two** | Planning, decisions | Fear of unknown, indecision |
| **Three** | Expansion, foresight | Obstacles, delays |
| **Four** | Celebration, harmony | Incomplete success |
| **Five** | Competition, conflict | Avoiding conflict |
| **Six** | Victory, recognition | Fall from grace, ego |
| **Seven** | Perseverance, defense | Overwhelmed, giving up |
| **Eight** | Swift action, movement | Delays, frustration |
| **Nine** | Resilience, persistence | Exhaustion, struggle |
| **Ten** | Burden, responsibility | Releasing burdens |
| **Page** | Enthusiasm, exploration | Setbacks, lack of direction |
| **Knight** | Energy, passion, adventure | Haste, scattered energy |
| **Queen** | Confidence, warmth, determination | Jealousy, selfishness |
| **King** | Leadership, vision, entrepreneur | Impulsiveness, tyranny |

### Cups (Water/Emotions)

| Card | Upright | Reversed |
|------|---------|----------|
| **Ace** | New love, intuition | Blocked emotions, emptiness |
| **Two** | Partnership, unity | Imbalance, tension |
| **Three** | Celebration, friendship | Overindulgence |
| **Four** | Contemplation, apathy | Taking action |
| **Five** | Loss, grief, regret | Acceptance, moving on |
| **Six** | Nostalgia, childhood | Living in past |
| **Seven** | Choices, illusion | Alignment, reality |
| **Eight** | Walking away, seeking | Aimless drifting |
| **Nine** | Satisfaction, contentment | Dissatisfaction |
| **Ten** | Harmony, family | Dysfunction, broken home |
| **Page** | Creativity, intuition | Emotional immaturity |
| **Knight** | Romance, charm | Moodiness, unrealistic |
| **Queen** | Compassion, nurturing | Insecurity, dependence |
| **King** | Emotional balance, diplomacy | Manipulation, coldness |

### Swords (Air/Mind)

| Card | Upright | Reversed |
|------|---------|----------|
| **Ace** | Clarity, breakthrough | Confusion, chaos |
| **Two** | Stalemate, avoidance | Decision time |
| **Three** | Heartbreak, grief | Recovery, forgiveness |
| **Four** | Rest, recuperation | Restlessness, burnout |
| **Five** | Conflict, defeat | Resolution, moving on |
| **Six** | Transition, moving on | Stagnation, resistance |
| **Seven** | Deception, strategy | Coming clean |
| **Eight** | Restriction, victim | Freedom, release |
| **Nine** | Anxiety, nightmares | Hope, recovery |
| **Ten** | Endings, rock bottom | Recovery, regeneration |
| **Page** | Curiosity, new ideas | Deception, manipulation |
| **Knight** | Action, ambition | Impulsive, reckless |
| **Queen** | Independence, perception | Cold, overly critical |
| **King** | Authority, truth | Manipulation, cruelty |

### Pentacles (Earth/Material)

| Card | Upright | Reversed |
|------|---------|----------|
| **Ace** | New opportunity, prosperity | Missed opportunity |
| **Two** | Balance, adaptability | Imbalance, disorganization |
| **Three** | Teamwork, learning | Lack of growth |
| **Four** | Security, possession | Greed, hoarding |
| **Five** | Hardship, poverty | Recovery, charity |
| **Six** | Generosity, sharing | Debt, selfishness |
| **Seven** | Assessment, patience | Impatience, bad investment |
| **Eight** | Diligence, skill | Perfectionism, shortcuts |
| **Nine** | Abundance, luxury | Setbacks, material loss |
| **Ten** | Wealth, inheritance | Family disputes, loss |
| **Page** | Ambition, opportunity | Lack of progress |
| **Knight** | Efficiency, routine | Boredom, stagnation |
| **Queen** | Nurturing, practicality | Self-neglect, smothering |
| **King** | Abundance, security | Greed, materialism |

---

## Decision Tree: Request Routing

```text
User Request
    │
    ├─ Card meanings?
    │   ├─ Major Arcana → [resources/major-arcana-guide.md]
    │   └─ Minor Arcana → [resources/minor-arcana-guide.md]
    │
    ├─ Spread design?
    │   ├─ Standard spreads → [resources/spreads-guide.md]
    │   └─ Custom spreads → [resources/spreads-guide.md]
    │
    ├─ Reading techniques?
    │   ├─ Interpretation methods → [resources/reading-techniques.md]
    │   └─ Timing with astrology → [resources/astro-tarot-timing.md]
    │
    ├─ Perform a reading?
    │   └─ [templates/template-tarot-reading.md]
    │
    └─ Other divination?
        └─ [resources/other-divination.md]
```

---

## Common Spreads

### Three-Card Spread

```
┌─────┐ ┌─────┐ ┌─────┐
│  1  │ │  2  │ │  3  │
│Past │ │Pres │ │Futr │
└─────┘ └─────┘ └─────┘
```

**Variations**:
- Past / Present / Future
- Situation / Action / Outcome
- Mind / Body / Spirit
- You / Other Person / Relationship

### Celtic Cross (10 Cards)

```
              ┌─────┐
              │  3  │ Above
              └─────┘
    ┌─────┐ ┌─────┐ ┌─────┐      ┌─────┐
    │  5  │ │ 1+2 │ │  6  │      │ 10  │ Outcome
    │Past │ │Cross│ │Futr │      └─────┘
    └─────┘ └─────┘ └─────┘      ┌─────┐
              ┌─────┐            │  9  │ Hopes/Fears
              │  4  │ Below      └─────┘
              └─────┘            ┌─────┐
                                 │  8  │ Environment
                                 └─────┘
                                 ┌─────┐
                                 │  7  │ Self
                                 └─────┘
```

**Positions**:
1. Present situation
2. Challenge/crossing
3. Crown (conscious)
4. Base (unconscious)
5. Recent past
6. Near future
7. Your approach
8. External influences
9. Hopes and fears
10. Outcome

---

## Reading Framework

### The What → Why → Action Pattern

Every card interpretation should include:

```
THE TOWER (Upright)

WHAT: A major upheaval or sudden change is disrupting your sense
of security. Structures you've built are being challenged or torn down.

WHY: This card appears because transformation is necessary. What
seemed stable was built on shaky foundations. The destruction
clears space for authentic rebuilding.

ACTION:
✓ DO: Let go of what's crumbling, don't resist necessary change
✓ DO: Look for the revelation hidden in the chaos
✗ DON'T: Try to rebuild what's falling - let it complete
✗ DON'T: Blame yourself - some upheavals are simply life events
```

---

## Astrological Timing

### Best Times for Readings

| Purpose | Moon Phase | Avoid |
|---------|-----------|-------|
| General guidance | Any | Void of Course |
| New beginnings | New Moon | Full Moon |
| Releasing/ending | Full Moon | New Moon |
| Relationships | Venus days (Friday) | Mars days |
| Career questions | Jupiter days (Thursday) | Saturn retrograde |
| Money questions | Venus/Jupiter days | Mercury retrograde |

### Planetary Hour Enhancement

For deeper readings, consider planetary hours:
- Mercury hours: Communication, decisions
- Venus hours: Love, relationships, beauty
- Mars hours: Action, conflict resolution
- Jupiter hours: Expansion, luck, big picture
- Saturn hours: Long-term, karma, structure

---

## Ethics & Guidelines

### Reading Ethics

```
FUNDAMENTAL PRINCIPLES:

1. EMPOWER, DON'T PREDICT
   - Cards show possibilities, not destinies
   - Reader facilitates, querent decides

2. DO NO HARM
   - Never predict death, illness, or tragedy
   - Refer to professionals for mental health concerns
   - Maintain confidentiality

3. HONESTY WITH COMPASSION
   - Deliver difficult messages constructively
   - Focus on growth and agency
   - Acknowledge card limitations

4. RESPECT FREE WILL
   - "If you continue on this path..." not "This will happen"
   - Multiple outcomes always possible
   - Human choice supersedes cards

5. BOUNDARIES
   - Third-party readings with caution
   - No readings for legal/medical advice
   - Recognize when to decline a reading
```

---

## Navigation

**Resources**
- [resources/major-arcana-guide.md](resources/major-arcana-guide.md) — Full Major Arcana meanings
- [resources/minor-arcana-guide.md](resources/minor-arcana-guide.md) — All 56 Minor Arcana cards
- [resources/spreads-guide.md](resources/spreads-guide.md) — Spread designs and positions
- [resources/reading-techniques.md](resources/reading-techniques.md) — Interpretation methods
- [resources/astro-tarot-timing.md](resources/astro-tarot-timing.md) — Astrological correspondences
- [resources/other-divination.md](resources/other-divination.md) — Oracle cards, I Ching, Runes

**Templates**
- [templates/template-tarot-reading.md](templates/template-tarot-reading.md) — Reading delivery format
- [templates/template-daily-card.md](templates/template-daily-card.md) — Daily card format

---

## Authoritative Sources

- **Rider-Waite-Smith Tradition** - Most common symbolic system
- **Thoth Tarot (Aleister Crowley)** - Esoteric/astrological
- **Marseilles Tradition** - Historical European
- [Biddy Tarot](https://www.biddytarot.com/) - Modern interpretation reference
- [Labyrinthos Academy](https://labyrinthos.co/) - Learning resources
- [Aeclectic Tarot](https://www.aeclectic.net/tarot/) - Deck database
