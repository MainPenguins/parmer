# Contributing to Parmer

Thanks for your interest in contributing to **Parmer**.

Parmer is an open-source, system-wide grammar checker for Linux. The goal is to provide a Grammarly-like experience on Linux without depending on browser extensions or application-specific integrations.

The project is currently in an early development stage. The most important part of the proof of concept is already working: Parmer can use **AT-SPI2** to observe text changes and caret movement in other applications and read the current text, cursor position, field name, and application name.

This document explains where the project is now, how it works, where it is going, and where contributors can help.

---

## Table of Contents

- [Project Status](#project-status)
- [What Is Parmer?](#what-is-parmer)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Architecture](#architecture)
- [Current Repository Structure](#current-repository-structure)
- [Current Progress](#current-progress)
- [Important AT-SPI2 Details](#important-at-spi2-details)
- [Development Roadmap](#development-roadmap)
- [Immediate Priorities](#immediate-priorities)
- [Areas Where You Can Contribute](#areas-where-you-can-contribute)
- [Development Setup](#development-setup)
- [Running the Current AT-SPI Prototype](#running-the-current-at-spi-prototype)
- [How the Current Text Tracking Works](#how-the-current-text-tracking-works)
- [Planned Grammar Checking Pipeline](#planned-grammar-checking-pipeline)
- [Privacy](#privacy)
- [Coding Guidelines](#coding-guidelines)
- [Git and Commit Guidelines](#git-and-commit-guidelines)
- [Issues and Pull Requests](#issues-and-pull-requests)
- [Contribution Checklist](#contribution-checklist)
- [Known Problems and Open Questions](#known-problems-and-open-questions)
- [Future Ideas](#future-ideas)
- [License](#license)

---

## Project Status

> **Current stage: Working AT-SPI2 text-tracking proof of concept**

Parmer is **not yet a complete grammar checker**.

The current project has successfully demonstrated the most important system-wide integration idea:

```text
Other Linux application
        ↓
      AT-SPI2
        ↓
  Parmer event listener
        ↓
    TextTracker
        ↓
text + cursor + application + field
```

The current prototype can receive events such as:

```text
object:text-changed:insert
object:text-caret-moved
```

and can retrieve:

- application name
- accessible field name
- current text
- caret/cursor position

The next major step is to turn this event stream into a stable text-processing pipeline and then connect it to a grammar engine.

### Current status at a glance

| Component | Status |
|---|---|
| Python project structure | 🟢 Started |
| AT-SPI2 integration | 🟢 Working PoC |
| Focus event handling | 🟢 Prototype |
| Text-change events | 🟢 Working |
| Caret tracking | 🟢 Working |
| Reading text from accessible objects | 🟢 Working |
| TextTracker | 🟢 Prototype |
| Debouncing | 🔴 Not implemented yet |
| Grammar engine abstraction | 🟡 Skeleton/planned |
| Local LanguageTool integration | 🟡 Skeleton/planned |
| Suggestion model | 🟡 Skeleton/planned |
| Suggestion UI | 🔴 Not implemented |
| GTK4/Libadwaita UI | 🔴 Not implemented |
| Packaging | 🔴 Not implemented |
| Settings | 🔴 Not implemented |
| Persian-specific checking | 🔴 Not implemented |
| Automated test suite | 🔴 Not implemented |
| Production reliability | 🔴 Not ready |

---

## What Is Parmer?

Parmer is intended to be a **system-wide grammar checker for Linux**.

Instead of integrating separately with Firefox, Chromium, Telegram, Discord, LibreOffice, GTK applications, Qt applications, etc., Parmer aims to use the Linux accessibility stack to obtain text from applications that expose their text fields through AT-SPI2.

The intended experience is:

```text
User types:

I has a apple

        ↓

Parmer observes the text

        ↓

Grammar engine detects:

"I has" → "I have"
"a apple" → "an apple"

        ↓

Parmer displays suggestions

        ↓

User accepts or ignores them
```

The application should feel like a native Linux utility rather than a browser-only extension.

---

## Goals

### Primary goals

1. Provide system-wide grammar checking on Linux.
2. Work across as many accessible applications as possible.
3. Use Linux-native accessibility APIs instead of global keyboard hooks.
4. Support Wayland-friendly architecture.
5. Keep user text private by default.
6. Prefer local processing where practical.
7. Provide a clean GTK4/Libadwaita interface.
8. Make the architecture modular so grammar engines can be replaced.
9. Make it possible to add language-specific engines later.
10. Keep the project understandable and contributor-friendly.

### Technical goals

The target architecture is:

```text
Applications
    ↓
AT-SPI2
    ↓
Accessibility layer
    ↓
TextTracker
    ↓
Debouncer
    ↓
Grammar Engine
    ↓
Suggestions
    ↓
GTK4 / Libadwaita UI
```

---

## Non-Goals

Parmer should not initially try to:

- implement a complete grammar engine from scratch
- intercept every keyboard event globally
- depend on X11-specific keyboard hooks
- send every character typed by the user to a remote server
- support every application perfectly from day one
- build the UI before the text-processing pipeline is reliable
- add AI just because it is available

The first objective is a reliable foundation.

---

# Architecture

## High-level architecture

```text
┌─────────────────────────────────────────────┐
│              User Applications              │
│                                             │
│ Firefox · Chromium · Telegram · GTK · Qt    │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
                ┌─────────────┐
                │   AT-SPI2   │
                └──────┬──────┘
                       │
                       ▼
             ┌───────────────────┐
             │ accessibility/    │
             │                   │
             │ Event listeners   │
             │ Focus handling    │
             │ Text access       │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │   TextTracker     │
             │                   │
             │ application       │
             │ field             │
             │ text              │
             │ cursor            │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │    Debouncer      │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │  Grammar Engine   │
             │                   │
             │ LanguageTool      │
             │ future engines    │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │    Suggestions    │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ GTK4 / Libadwaita │
             │                   │
             │ Overlay           │
             │ Popover           │
             │ Tray              │
             └───────────────────┘
```

---

# Current Repository Structure

```text
parmer/
├── accessibility/
│   ├── __init__.py
│   ├── atspi.py
│   ├── focus.py
│   └── text.py
│
├── core/
│   ├── checker.py
│   ├── context.py
│   ├── language.py
│   ├── suggestions.py
│   └── text_tracker.py
│
├── engines/
│   ├── languagetool.py
│   └── local.py
│
├── ui/
│   ├── overlay.py
│   ├── suggestion_popover.py
│   └── tray.py
│
├── LICENSE
├── main.py
└── readme.md
```

The codebase is intentionally separated into layers.

## `accessibility/`

This package is responsible for communicating with the Linux accessibility stack.

It should contain:

- AT-SPI initialization
- event listeners
- focus tracking
- text interface access
- accessibility-specific error handling

It should **not** contain grammar-checking logic.

---

## `core/`

This is where Parmer's application-independent logic belongs.

Examples:

- tracking the current text field
- debouncing
- language detection/selection
- grammar-checking orchestration
- context management
- suggestion representation

The core should ideally not need to know whether text came from Telegram, Chromium, GTK, Qt, or another application.

---

## `engines/`

Grammar engines live here.

The initial intended engine is a local LanguageTool integration.

The long-term goal is to make engines interchangeable:

```text
Grammar Engine
├── Local LanguageTool
├── Custom/Persian engine
├── Other local engines
└── Optional remote/AI engine
```

---

## `ui/`

All user-facing GTK4/Libadwaita components belong here.

Planned responsibilities include:

- suggestion popovers
- correction overlays
- system tray/status interface
- settings
- language selection
- enable/disable controls

The UI should not directly implement AT-SPI logic.

---

# Current Progress

## 1. AT-SPI application discovery

The prototype successfully discovered accessible applications through AT-SPI.

Examples observed during development included:

- Chromium
- Telegram
- TelegramDesktop
- GitHub Desktop
- GNOME components
- other accessible applications

This proved that Parmer can see the system accessibility tree.

---

## 2. Focus events

Parmer can listen for focus-related accessibility events.

Many focus events are generated for objects that are not text fields.

For example:

```text
window
panel
filler
text
```

Therefore the accessibility layer filters objects and only processes relevant text objects.

---

## 3. Text-change events

The prototype successfully receives events such as:

```text
object:text-changed:insert
```

This is the core signal needed to know that the user changed text.

Example observed event:

```text
Event type : object:text-changed:insert
Source     : Caption
Role       : text
Cursor     : 6
```

---

## 4. Caret events

The prototype also receives:

```text
object:text-caret-moved
```

Caret positions were observed changing as text was entered.

This gives Parmer the information required to associate the current grammar suggestions with the cursor position.

---

## 5. Reading the actual text

A particularly important implementation detail was discovered while testing PyGObject's AT-SPI bindings.

`Atspi.Accessible` has an overridden `get_text()` method:

```python
Atspi.Accessible.get_text(self) -> Atspi.Text
```

This is **not** the same as the actual `Atspi.Text.get_text()` method:

```python
Atspi.Text.get_text(
    self,
    start_offset,
    end_offset
) -> str
```

Because `Atspi.Accessible` also implements the `Atspi.Text` interface, calling:

```python
obj.get_text(0, character_count)
```

can incorrectly resolve to the `Accessible.get_text()` override.

The working approach is to call the interface method directly:

```python
Atspi.Text.get_text(
    obj,
    0,
    character_count
)
```

Likewise:

```python
Atspi.Text.get_caret_offset(obj)
```

and:

```python
Atspi.Text.get_character_count(obj)
```

This distinction is important for anyone modifying the AT-SPI text code.

---

# Current TextTracker

The current working concept is a `TextTracker` that stores the state of the currently observed text object.

Conceptually:

```python
class TextTracker:
    def __init__(self):
        self.application = None
        self.field = None
        self.text = ""
        self.cursor = 0
```

When an accessible object changes, the tracker obtains:

```text
application
field
cursor
text
```

The current implementation uses the AT-SPI `Text` interface directly.

---

# Development Roadmap

The roadmap is intentionally incremental.

## Phase 0 — Foundation

### Status: 🟢 In progress / largely complete

- [x] Create repository
- [x] Create Python project structure
- [x] Create accessibility layer
- [x] Initialize AT-SPI
- [x] Discover accessible applications
- [x] Listen for focus changes
- [x] Listen for text changes
- [x] Listen for caret movement
- [x] Detect text objects
- [x] Read current text
- [x] Read caret position
- [x] Track application name
- [x] Track field name

---

# Phase 1 — Robust Text Tracking

### Status: 🟡 Next priority

This phase should make the current PoC reliable enough to become the foundation of the rest of Parmer.

### Tasks

- [ ] Separate AT-SPI event handling from text state management
- [ ] Make `TextTracker` independent from UI
- [ ] Handle disappearing accessibility objects safely
- [ ] Handle invalid/stale AT-SPI object paths
- [ ] Handle focus changes cleanly
- [ ] Ignore irrelevant accessibility roles
- [ ] Detect when the active text field changes
- [ ] Avoid unnecessary full-text reads
- [ ] Track previous text
- [ ] Track text changes/diffs where useful
- [ ] Track selection state
- [ ] Track cursor movement
- [ ] Handle applications that expose incomplete accessibility data
- [ ] Add structured event/state objects instead of relying on debug printing

### Important

The AT-SPI layer should not crash if an application closes, a text field disappears, or an accessibility object becomes invalid.

For example, during development an object disappeared between receiving an event and reading it. This can result in an AT-SPI/GLib error such as:

```text
No such object path
```

This should be treated as a recoverable condition.

---

# Phase 2 — Debouncing

### Status: 🔴 Not implemented

A grammar checker must **not** run after every keystroke.

Without debouncing:

```text
H
He
Hel
Hell
Hello
```

could produce five grammar-check requests.

Instead:

```text
User types
     ↓
TextTracker updates
     ↓
wait briefly
     ↓
user stops typing
     ↓
Grammar check
```

### Tasks

- [ ] Implement a debouncer
- [ ] Make delay configurable
- [ ] Cancel outdated checks
- [ ] Avoid checking unchanged text
- [ ] Prevent race conditions between old and new checks
- [ ] Decide how cursor movement should interact with pending checks

A likely starting point is a short idle delay after the latest text change.

---

# Phase 3 — Grammar Engine Abstraction

### Status: 🟡 Skeleton exists

The core should not directly depend on LanguageTool.

Instead:

```text
Checker
   ↓
GrammarEngine interface
   ↓
┌──────────────────────┐
│ LanguageTool         │
│ Future engines       │
└──────────────────────┘
```

The abstraction should make it possible to replace the engine later.

Possible conceptual API:

```python
check(text, language)
```

returning structured suggestions.

---

# Phase 4 — Local LanguageTool

### Status: 🟡 Planned

The first practical grammar engine should be **local LanguageTool**.

The initial objective is:

```text
Parmer
  ↓
Local LanguageTool
  ↓
Matches
  ↓
Suggestions
```

### Requirements

- [ ] Run LanguageTool locally
- [ ] Create Python integration
- [ ] Send text to the local engine
- [ ] Parse grammar matches
- [ ] Convert matches into Parmer suggestion objects
- [ ] Preserve offsets
- [ ] Preserve replacement candidates
- [ ] Preserve useful rule/category information
- [ ] Handle engine errors
- [ ] Avoid blocking the UI/event loop

The engine must not block AT-SPI event processing.

---

# Phase 5 — Suggestion Model

### Status: 🟡 Planned

Create a clean internal representation for suggestions.

A suggestion should eventually contain information similar to:

```text
start offset
end offset
original text
replacement(s)
message
rule/category
confidence/priority if available
```

For example:

```text
Text:
I has a cat

Suggestion:
"I has"
    ↓
"I have"
```

The UI should consume these objects without knowing anything about LanguageTool internals.

---

# Phase 6 — Correction UI

### Status: 🔴 Not implemented

Build the first GTK4/Libadwaita interface.

Possible UI:

```text
              ┌──────────────────────┐
              │ has → have           │
              │                      │
              │ I have a cat         │
              └──────────────────────┘
```

Potential components:

- [ ] suggestion popover
- [ ] correction action
- [ ] dismiss action
- [ ] ignore rule
- [ ] ignore word
- [ ] suggestion navigation
- [ ] positioning near the text/caret
- [ ] accessibility-friendly controls

The exact visual design should be decided after the underlying data flow works.

---

# Phase 7 — Applying Corrections

### Status: 🔴 Not implemented

Once a suggestion is selected, Parmer needs to modify the text in the target application.

The preferred approach is to use accessibility APIs where possible rather than simulating keyboard input.

Potential path:

```text
Suggestion
    ↓
AT-SPI EditableText
    ↓
replace selected range
```

This needs careful testing because not every application exposes the same capabilities.

### Tasks

- [ ] Detect editable text support
- [ ] Test `EditableText`
- [ ] Replace text ranges
- [ ] Preserve cursor position
- [ ] Handle applications that expose read-only text
- [ ] Fall back gracefully when modification is unavailable

---

# Phase 8 — Context Awareness

### Status: 🔴 Not implemented

Grammar checking should eventually understand enough context to avoid unnecessary or incorrect checks.

Potential context:

```text
Application
Window
Text field
Language
Cursor
Selection
Surrounding text
```

For example, Parmer may eventually distinguish:

```text
chat message
code editor
URL field
password field
search field
email composer
document editor
```

This should be implemented carefully and conservatively.

---

# Phase 9 — Language Support

### Status: 🔴 Not implemented

The first implementation should focus on getting the architecture stable.

After that:

- [ ] language selection
- [ ] automatic language detection
- [ ] multiple-language support
- [ ] Persian support
- [ ] Persian-specific rules
- [ ] language-specific engines

Persian is an important future direction, but it should not force the core architecture to become language-specific.

---

# Phase 10 — Privacy and Settings

### Status: 🔴 Not implemented

Create a settings system for:

- [ ] enable/disable Parmer
- [ ] language
- [ ] grammar engine
- [ ] debounce delay
- [ ] ignored applications
- [ ] ignored fields
- [ ] ignored words/rules
- [ ] privacy settings
- [ ] optional online engines

Privacy should be explicit and understandable.

---

# Phase 11 — Packaging

### Status: 🔴 Not implemented

Eventually Parmer should be installable without cloning the repository.

Potential targets:

- [ ] Debian/Ubuntu package
- [ ] Flatpak
- [ ] AppImage if useful
- [ ] distribution packages
- [ ] desktop entry
- [ ] autostart/background service
- [ ] uninstall support

Packaging should be designed around the actual AT-SPI and GTK runtime requirements.

---

# Phase 12 — Production Hardening

### Status: 🔴 Future

Before calling Parmer production-ready:

- [ ] automated tests
- [ ] integration tests
- [ ] memory leak investigation
- [ ] CPU usage testing
- [ ] large-text testing
- [ ] application compatibility testing
- [ ] accessibility failure handling
- [ ] crash recovery
- [ ] logging
- [ ] configurable debug mode
- [ ] packaging tests
- [ ] Wayland testing
- [ ] multiple desktop environment testing

---

# Immediate Priorities

If you want to contribute **right now**, these are the most useful areas.

## Priority 1 — TextTracker reliability

Improve:

```text
accessibility events
        ↓
TextTracker
```

Focus on:

- stale objects
- focus changes
- text changes
- cursor movement
- selection
- application switching
- error recovery

---

## Priority 2 — Debouncer

Build:

```text
TextTracker
     ↓
Debouncer
```

The debouncer should prevent the grammar engine from running on every character.

---

## Priority 3 — LanguageTool integration

Implement the local engine:

```text
core/checker.py
       ↓
engines/languagetool.py
```

Keep it asynchronous/non-blocking where possible.

---

## Priority 4 — Suggestion model

Create a clean representation of grammar suggestions.

Do not couple the suggestion model directly to LanguageTool.

---

## Priority 5 — Tests

Add tests around:

- text tracking
- offset handling
- debouncing
- suggestion parsing
- grammar engine results
- context handling

---

# Areas Where You Can Contribute

You do not need to work on the whole project.

Good contribution areas include:

### Accessibility

- AT-SPI event handling
- focus tracking
- text extraction
- EditableText support
- application compatibility

### Core

- TextTracker
- debouncer
- context handling
- language management
- checker orchestration
- suggestion data structures

### Grammar Engines

- LanguageTool
- alternative local engines
- Persian grammar support
- language-specific processing

### UI

- GTK4
- Libadwaita
- suggestion popovers
- overlays
- settings
- system tray/status UI

### Testing

- unit tests
- integration tests
- application compatibility
- Wayland testing
- accessibility edge cases

### Documentation

- architecture documentation
- setup guides
- troubleshooting
- application compatibility reports
- language support documentation

### Packaging

- Flatpak
- Debian packaging
- desktop integration
- autostart

---

# Development Setup

Parmer is currently developed primarily with Python.

A Linux environment with:

- Python 3
- PyGObject
- AT-SPI2
- GTK4/Libadwaita for future UI work

is expected.

On systems where multiple Python installations exist, make sure the Python interpreter has the required GObject/AT-SPI bindings.

For example, the current development environment uses the system Python:

```bash
/usr/bin/python3
```

rather than the separate Linuxbrew Python installation, because the system interpreter has the required GTK/AT-SPI Python bindings available.

---

# Running the Current AT-SPI Prototype

From the repository root:

```bash
/usr/bin/python3 -m accessibility.atspi
```

You should see:

```text
Parmer AT-SPI listener started.
Waiting for text input...
```

Then focus a text field in an accessible application and type.

The current prototype should receive events similar to:

```text
object:text-changed:insert
object:text-caret-moved
```

and print information about the active text object.

---

# How the Current Text Tracking Works

The important part of the current implementation is the distinction between `Atspi.Accessible` and the `Atspi.Text` interface.

An accessible object can implement the Text interface:

```text
Atspi.Accessible
       │
       └── Atspi.Text
```

However, PyGObject's `Accessible.get_text()` is an overridden method with a different meaning:

```python
Atspi.Accessible.get_text(self) -> Atspi.Text
```

The actual Text interface method is:

```python
Atspi.Text.get_text(
    self,
    start_offset,
    end_offset
) -> str
```

Therefore the current code intentionally uses:

```python
Atspi.Text.get_text(obj, 0, character_count)
```

instead of:

```python
obj.get_text(0, character_count)
```

The same approach is used for the caret and character count:

```python
Atspi.Text.get_caret_offset(obj)

Atspi.Text.get_character_count(obj)
```

This is an important implementation detail. Do not casually replace these calls with `obj.get_text(...)` without verifying the installed PyGObject bindings.

---

# Planned Grammar Checking Pipeline

The intended flow is:

```text
User types
    │
    ▼
AT-SPI text-changed event
    │
    ▼
TextTracker
    │
    ▼
Debouncer
    │
    ▼
Current text snapshot
    │
    ▼
Grammar Checker
    │
    ▼
Grammar Engine
    │
    ▼
Suggestion objects
    │
    ▼
UI
```

The event listener should remain fast.

Heavy work should happen outside the event callback whenever possible.

---

# Privacy

Parmer is intended to be **privacy-first**.

Text entered into applications can contain:

- private conversations
- passwords or sensitive information
- work documents
- personal information
- financial information
- source code

Therefore the architecture should prefer local processing.

The initial grammar engine is planned to run locally.

Online services or AI-based engines may be considered later, but they should be:

- explicitly opt-in
- clearly identified
- configurable
- documented
- disabled by default unless there is a strong reason otherwise

Do not introduce network transmission of user text without discussing the privacy implications.

---

# Coding Guidelines

## Keep responsibilities separated

Avoid putting everything into `main.py`.

Prefer:

```text
accessibility/
    accessibility concerns

core/
    application logic

engines/
    grammar engines

ui/
    user interface
```

---

## Keep the core independent

For example, `core/checker.py` should not need to know that text originally came from Telegram.

It should receive structured data.

---

## Avoid premature abstraction

Do not create a framework for a feature that does not exist yet.

Build the smallest clean abstraction that solves the current problem.

---

## Avoid unnecessary dependencies

Before adding a dependency, consider:

- Can the standard library solve this?
- Is the dependency maintained?
- Does it work well on Linux?
- Does it work with Wayland?
- Does it add significant complexity?
- Is it required for the feature?

---

## Do not use global keyboard hooks for the core architecture

Parmer is intended to use AT-SPI2 for system-wide text access.

Avoid designing core functionality around global key interception.

This is particularly important for modern Wayland environments.

---

## Handle accessibility failures gracefully

Applications can:

- disappear
- restart
- expose incomplete accessibility trees
- provide stale objects
- expose read-only text
- implement accessibility differently

None of these should make Parmer crash.

---

# Git and Commit Guidelines

Keep commits focused.

Good:

```text
feat: add AT-SPI text tracking
fix: handle stale accessibility objects
feat: add text debouncer
feat: add LanguageTool engine
test: add TextTracker tests
```

Avoid mixing unrelated changes into one commit.

For example, do not combine:

```text
UI redesign
+ AT-SPI rewrite
+ packaging
+ unrelated formatting
```

in one commit.

---

# Issues and Pull Requests

Before opening a PR:

1. Explain what the change does.
2. Explain why it is needed.
3. Keep the PR focused.
4. Test the changed functionality.
5. Mention known limitations.
6. Include screenshots for UI changes when useful.
7. Include reproduction steps for bug fixes.

A useful PR description should answer:

```text
What changed?

Why?

How was it tested?

What remains?

Does it introduce any new dependency or privacy concern?
```

---

# Contribution Checklist

Before submitting a PR:

- [ ] The change has a clear purpose.
- [ ] The code follows the project structure.
- [ ] No unrelated changes are included.
- [ ] Existing functionality still works.
- [ ] New behavior has been tested.
- [ ] Errors are handled appropriately.
- [ ] No unnecessary dependency was introduced.
- [ ] No user text is sent to an external service unexpectedly.
- [ ] Documentation was updated if necessary.
- [ ] The PR description explains the change.

---

# Known Problems and Open Questions

These are intentionally open for contributors.

## AT-SPI compatibility

Different applications expose accessibility information differently.

Questions to investigate:

- Which GTK applications expose editable text reliably?
- How well does Chromium expose text fields?
- How well does Firefox expose text fields?
- How well does Telegram expose text fields?
- How do Qt applications behave?
- Which applications expose selection information?
- Which applications support EditableText?

---

## Object lifetime

AT-SPI objects can disappear between receiving an event and processing it.

The system needs robust handling for:

```text
event received
      ↓
object disappears
      ↓
read operation fails
```

This should be treated as a normal recoverable condition.

---

## Performance

The system must remain lightweight.

Potential performance concerns:

- event frequency
- large text fields
- frequent cursor movement
- grammar-check frequency
- LanguageTool latency
- UI updates

---

## Text offsets

Grammar engines return offsets into strings.

AT-SPI also uses offsets.

Parmer needs to carefully preserve these offsets when:

- text changes
- Unicode characters are involved
- corrections are applied
- cursor moves
- multiple suggestions exist

Unicode and multilingual text must be tested thoroughly.

---

## Password fields

Parmer must avoid processing sensitive fields such as password inputs.

This should be handled conservatively at the accessibility layer/context layer.

---

# Future Ideas

These are ideas, not current commitments.

## Persian grammar checking

A dedicated Persian grammar system could eventually be added.

Possible architecture:

```text
Persian text
     ↓
Language detection
     ↓
Persian engine
     ↓
Suggestions
```

---

## Optional AI engine

AI could eventually provide:

- rewriting
- style suggestions
- advanced contextual corrections
- explanations

However, this should remain separate from the basic local grammar-checking pipeline.

A user should be able to use Parmer without sending their text to an AI service.

---

## Per-application configuration

Possible settings:

```text
Telegram      enabled
Browser       enabled
Code editor   disabled
Password      disabled
Terminal      disabled
```

---

## Custom dictionaries

Possible features:

- personal dictionary
- technical vocabulary
- programming terms
- names
- ignored words

---

## Writing style

Future style checks could include:

- repeated words
- passive voice
- readability
- unnecessary words
- punctuation
- tone

These should be separate from the core grammar engine.

---

# Suggested Milestones

A practical development sequence is:

```text
M0  AT-SPI proof of concept
 │
 ├── event listening
 ├── focus tracking
 ├── text reading
 └── caret tracking
 │
 ▼
M1  Reliable TextTracker
 │
 ├── state management
 ├── object lifetime
 ├── selection
 └── application compatibility
 │
 ▼
M2  Debouncer
 │
 ▼
M3  Grammar engine abstraction
 │
 ▼
M4  Local LanguageTool
 │
 ▼
M5  Suggestion model
 │
 ▼
M6  GTK4/Libadwaita UI
 │
 ▼
M7  Applying corrections
 │
 ▼
M8  Settings + privacy controls
 │
 ▼
M9  Packaging
 │
 ▼
M10 Production hardening
```

---

# How to Pick a Task

If you are new to the project, start with one of these:

### Beginner-friendly

- improve documentation
- add tests
- investigate application compatibility
- improve error messages
- add logging
- document AT-SPI behavior

### Intermediate

- TextTracker improvements
- debouncer
- suggestion data model
- LanguageTool integration
- application compatibility handling

### Advanced

- AT-SPI edge cases
- EditableText correction
- asynchronous architecture
- performance optimization
- packaging
- accessibility compatibility across desktop environments

---

# Final Note

Parmer is currently at a very early but important stage.

The system-wide text acquisition problem has been successfully demonstrated through AT-SPI2. The next goal is not to immediately build a huge UI or add AI; it is to turn the working prototype into a reliable pipeline:

```text
AT-SPI2
   ↓
TextTracker
   ↓
Debouncer
   ↓
Grammar Engine
   ↓
Suggestions
   ↓
UI
```

Contributions are welcome at every layer.

If you want to work on something that is not explicitly listed here, open an issue first and describe the idea. This helps keep the architecture coherent while the project is still taking shape.

**Thanks for helping build a proper Linux-native grammar checker. 🐧**
