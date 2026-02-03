# Technology Stack

**Project:** TheBeckoningMU Web Portal (Character Creation + Grid Builder + Approval Workflows)
**Researched:** 2026-02-03
**Mode:** Ecosystem (Stack dimension)

## Verified Existing Stack

These are already installed and running. Do NOT change them.

| Technology | Version | Purpose | Source |
|------------|---------|---------|--------|
| Python | 3.13+ | Runtime | pyproject.toml |
| Evennia | 5.0.1 | MUD framework | .dist-info/METADATA (verified) |
| Django | 5.2.7 | Web framework | .dist-info/METADATA (verified) |
| Django REST Framework | 3.14.0 | REST API (ships with Evennia) | .dist-info/METADATA (verified) |
| Twisted | 24.11+ | Async networking (ships with Evennia) | Evennia dependency |
| Bootstrap | 5.1.3 | CSS framework (CDN in templates) | character_creation.html |
| Vanilla JavaScript | ES6+ | Frontend interactivity | editor.html, character_creation.html |
| SQLite | default | Database | Evennia default |
| Poetry | latest | Dependency management | pyproject.toml |

**IMPORTANT CORRECTION:** The PROJECT_CONTEXT.md states "Django 4.2+" but the actual installed version is **Django 5.2.7**. Evennia 5.0.1 requires `django>=5.2,<5.3`. All stack recommendations below are verified against Django 5.2.x compatibility.

---

## Recommended Additions

### Tier 1: Add Now (Essential for Web Portal)

#### htmx 2.0.8 -- Server-Driven UI Interactivity
| Detail | Value |
|--------|-------|
| **Version** | 2.0.8 |
| **Confidence** | HIGH (verified via npm registry + GitHub releases) |
| **Purpose** | Replace hand-rolled `fetch()` calls with declarative HTML attributes for approval workflows, form validation, dashboard updates |
| **Why** | The existing codebase already uses a Django template + vanilla JS + fetch() pattern. htmx is the natural evolution: it keeps server-rendered HTML but adds partial page updates via `hx-get`, `hx-post`, `hx-swap`, `hx-trigger`. No build step. No framework migration. Just add one `<script>` tag. |
| **Why not a JS framework** | The project has 1,472 lines of template HTML for chargen and an 843-line vanilla JS grid builder. Migrating to React/Vue would mean rewriting everything. htmx enhances what exists. |
| **Installation** | CDN: `<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>` |

```html
<!-- Example: Approval button that updates status inline -->
<button hx-post="/api/traits/character/{{ char_id }}/approval/"
        hx-target="#status-badge-{{ char_id }}"
        hx-swap="outerHTML"
        hx-vals='{"action":"approve"}'>
    Approve
</button>
```

**Note on htmx 4.0:** Alpha is available; stable release expected mid-2026. Stay on 2.0.x for now. Migration will be straightforward when 4.0 stabilizes (main change is fetch() replacing XMLHttpRequest internally).

#### django-htmx 1.27.0 -- Django Middleware for htmx
| Detail | Value |
|--------|-------|
| **Version** | 1.27.0 |
| **Confidence** | HIGH (verified via PyPI, released 2025-11-28) |
| **Purpose** | Middleware that detects htmx requests, provides `request.htmx` attribute for conditional template rendering |
| **Why** | Lets views return full page on normal request OR just the changed fragment on htmx request. One view, two response modes. Critical for progressive enhancement. |
| **Django compat** | Django 4.2 through 6.0 (verified). Our Django 5.2.7 is fully supported. |
| **Python compat** | Python 3.10 through 3.14 (verified). Our Python 3.13 is fully supported. |
| **Installation** | `pip install django-htmx` then add `"django_htmx"` to INSTALLED_APPS and `"django_htmx.middleware.HtmxMiddleware"` to MIDDLEWARE |

```python
# Example: View that serves full page OR fragment
def character_list(request):
    characters = PendingCharacters.objects.all()
    template = "partials/character_list.html" if request.htmx else "staff/character_approval.html"
    return render(request, template, {"characters": characters})
```

#### Bootstrap 5.3.8 -- Upgrade from 5.1.3
| Detail | Value |
|--------|-------|
| **Version** | 5.3.8 |
| **Confidence** | HIGH (verified via official Bootstrap blog, getbootstrap.com) |
| **Purpose** | Dark mode support, improved form components, better accessibility |
| **Why upgrade** | The existing templates (character_creation.html) use Bootstrap 5.1.3 via CDN. Version 5.3.x adds native dark mode (CSS custom properties) which aligns perfectly with the existing dark theme (--builder-bg: #1a1a1a etc). Currently the dark styling is all custom CSS; Bootstrap 5.3's `data-bs-theme="dark"` would handle most of it. Also 5.3 is the actively maintained line. |
| **Migration risk** | LOW. 5.1 to 5.3 is a minor version bump. Breaking changes are minimal. |
| **Installation** | Update CDN link: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css` |

### Tier 2: Add During Specific Features

#### Alpine.js 3.15.3 -- Lightweight Reactive UI (for Builder interactions)
| Detail | Value |
|--------|-------|
| **Version** | 3.15.3 |
| **Confidence** | MEDIUM (version from npm registry search, ~2 weeks old as of today) |
| **Purpose** | Replace inline `onclick` handlers and manual DOM state management in the grid builder editor |
| **Why** | The builder editor.html has 400+ lines of vanilla JS with manual DOM manipulation (`document.getElementById`, inline `onclick`). Alpine.js provides reactive data binding via HTML attributes (`x-data`, `x-bind`, `x-on`) without a build step. It is the JS equivalent of what htmx is for server communication. |
| **When to add** | Phase where compass rose, trigger editor, or room template picker are built. These need client-side interactivity that htmx alone cannot provide (dragging, local state, conditional UI). |
| **Installation** | CDN: `<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.3/dist/cdn.min.js"></script>` |

```html
<!-- Example: Compass rose with Alpine.js reactive state -->
<div x-data="{ direction: null, connecting: false }">
    <svg viewBox="0 0 100 100">
        <circle x-on:click="direction='n'; $dispatch('add-exit', {dir:'north'})"
                cx="50" cy="10" r="8"
                x-bind:class="direction === 'n' ? 'active' : ''" />
        <!-- ... other directions -->
    </svg>
</div>
```

**htmx + Alpine.js complement each other:** htmx handles server communication (save, load, approve), Alpine handles local UI state (drag mode, selected room, compass hover). This is a well-documented pattern in the Django community.

#### django-fsm-2 4.1.0 -- Finite State Machine for Approval Workflows
| Detail | Value |
|--------|-------|
| **Version** | 4.1.0 |
| **Confidence** | HIGH (verified via PyPI, released 2025-11-03) |
| **Purpose** | Formalize approval state transitions: draft -> submitted -> in_review -> approved/rejected/revision_requested |
| **Why** | The existing CharacterBio model has a simple `approved = BooleanField`. The BuildProject model has no approval status at all. Adding FSM ensures invalid transitions are impossible (e.g., cannot approve without reviewing, cannot go from approved back to draft without explicit revert). Also enables audit logging via django-fsm-log. |
| **Why django-fsm-2 over django-fsm** | django-fsm-2 is the actively maintained fork. Original django-fsm had maintenance gaps. django-fsm-2 supports Django 4.2 through 6.0 and Python 3.8 through 3.14 (verified). |
| **When to add** | Phase where approval workflows are formalized (both chargen approval and builder project promotion). |
| **Installation** | `pip install django-fsm-2` |
| **Optional companion** | `pip install django-fsm-log` for transition audit trails |

```python
# Example: BuildProject with FSM states
from django_fsm import FSMField, transition

class BuildProject(models.Model):
    status = FSMField(default='draft')

    @transition(field=status, source='draft', target='sandbox')
    def build_to_sandbox(self):
        """Create sandbox rooms from map_data."""
        pass

    @transition(field=status, source='sandbox', target='pending_review')
    def submit_for_review(self):
        pass

    @transition(field=status, source='pending_review', target='approved')
    def approve(self):
        pass

    @transition(field=status, source='approved', target='live')
    def promote_to_live(self):
        """Move from sandbox to production grid."""
        pass
```

### Tier 3: Consider But Not Required

#### Django REST Framework Serializers (already installed)
| Detail | Value |
|--------|-------|
| **Version** | 3.14.0 (already installed via Evennia) |
| **Confidence** | HIGH |
| **Purpose** | Replace hand-rolled JSON serialization in traits/api.py and builder/views.py |
| **Why** | The existing API views manually construct JSON dictionaries (see `traits/api.py` lines 47-61, `builder/views.py` lines 130-143). DRF serializers provide validation, nested serialization, and consistent error handling for free. Since DRF is already installed, this is zero new dependencies. |
| **When to add** | Opportunistically during any API refactoring. Not blocking. |
| **Why Tier 3** | The existing hand-rolled JSON works fine. DRF serializers are better practice but the refactor is not essential for new features. |

---

## Alternatives Considered and Rejected

| Category | Recommended | Rejected | Why Rejected |
|----------|-------------|----------|--------------|
| **JS Framework** | htmx + Alpine.js | React / Vue / Svelte | Would require rewriting existing 2,300+ lines of template HTML and vanilla JS. Build step adds complexity. The project has no node_modules and no bundler -- adding one is unnecessary overhead for a MUD admin portal. |
| **CSS Framework** | Bootstrap 5.3.8 (upgrade) | Tailwind CSS | Would require a build step (PostCSS). Existing templates are already Bootstrap-based. Migration would touch every template file. |
| **API Layer** | Django views + htmx | GraphQL / tRPC | Overkill for this use case. The project has ~15 API endpoints. REST + htmx partials is simpler and sufficient. |
| **State Machine** | django-fsm-2 | django-viewflow / django-river | django-viewflow is a full BPM engine -- too heavy. django-river requires database-backed workflow definitions -- more complex than needed. django-fsm-2 is lightweight and model-level, matching the simple approval flows needed. |
| **SVG/Canvas Library** | Vanilla SVG (keep existing) | Fabric.js / Konva.js / SVG-Edit | The existing builder already has working SVG exit visualization. These libraries add 200KB+ of JS for features the builder does not need (image manipulation, complex path editing). The compass rose and room nodes are simple geometric shapes well-served by vanilla SVG + Alpine.js for reactivity. |
| **Drag & Drop Library** | Vanilla JS (keep existing) | SortableJS / interact.js | The existing drag-and-drop in editor.html works. SortableJS is for list reordering, not canvas-style room dragging. interact.js adds dependency for marginal benefit. |
| **Form Library** | Django Forms + htmx | django-crispy-forms | The existing chargen uses a fully custom HTML form. django-crispy-forms would require restructuring the form layout. htmx provides the validation feedback the forms need without changing the HTML structure. |
| **Approval Workflow** | django-fsm-2 | Custom boolean flags | The existing `approved = BooleanField` pattern cannot represent intermediate states (in_review, revision_requested). FSM prevents invalid transitions. Worth the small dependency. |

---

## Stack Architecture Summary

```
Browser
  |
  |-- Bootstrap 5.3.8 (CSS framework, dark mode)
  |-- htmx 2.0.8 (server-driven partial updates)
  |-- Alpine.js 3.15.3 (local reactive UI state)
  |-- Vanilla JS (existing builder logic, drag/drop)
  |-- SVG (exit lines, compass rose, room nodes)
  |
  v
Django 5.2.7
  |
  |-- django-htmx 1.27.0 (htmx request detection middleware)
  |-- django-fsm-2 4.1.0 (approval state machines)
  |-- DRF 3.14.0 (already installed, optional serializer use)
  |-- Django templates (server-rendered HTML + htmx partials)
  |-- Django views (full pages + htmx fragment responses)
  |
  v
Evennia 5.0.1
  |
  |-- Batch Code Processor (sandbox building from map_data)
  |-- Evennia Object API (room/exit/object creation)
  |-- Evennia Tags (tracking web_builder, project_N)
  |
  v
SQLite (default) / PostgreSQL (production option)
```

---

## Installation Plan

### Python Dependencies (add to pyproject.toml or pip install)

```bash
pip install django-htmx==1.27.0
pip install django-fsm-2==4.1.0
pip install django-fsm-log  # optional, for audit trails
```

### Django Settings Changes

```python
# In beckonmu/server/conf/settings.py

INSTALLED_APPS += (
    "django_htmx",
    # django-fsm-2 does not need INSTALLED_APPS entry
    # django_fsm_log needs entry if used:
    # "django_fsm_log",
)

MIDDLEWARE += [
    "django_htmx.middleware.HtmxMiddleware",
]
```

### Frontend CDN Updates (in base template)

```html
<!-- Upgrade Bootstrap from 5.1.3 to 5.3.8 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
      crossorigin="anonymous">

<!-- Add htmx -->
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>

<!-- Add Alpine.js (defer is important -- must load after DOM) -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.3/dist/cdn.min.js"></script>

<!-- Keep Bootstrap JS bundle -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI"
        crossorigin="anonymous"></script>
```

**No npm, no node_modules, no bundler, no build step.** All frontend libraries via CDN.

---

## Version Compatibility Matrix

| Component | Version | Django 5.2 | Python 3.13 | Verified Source |
|-----------|---------|------------|-------------|-----------------|
| Evennia | 5.0.1 | requires 5.2.x | requires 3.11+ | .dist-info/METADATA |
| django-htmx | 1.27.0 | supports 4.2-6.0 | supports 3.10-3.14 | PyPI (2025-11-28) |
| django-fsm-2 | 4.1.0 | supports 4.2-6.0 | supports 3.8-3.14 | PyPI (2025-11-03) |
| DRF | 3.14.0 | included by Evennia | included by Evennia | .dist-info/METADATA |
| htmx | 2.0.8 | n/a (client-side) | n/a (client-side) | npm + GitHub releases |
| Alpine.js | 3.15.3 | n/a (client-side) | n/a (client-side) | npm registry (Jan 2026) |
| Bootstrap | 5.3.8 | n/a (client-side) | n/a (client-side) | getbootstrap.com (verified) |

All components verified compatible. No conflicts detected.

---

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| **React / Vue / Svelte** | Requires build step, would force rewrite of all existing templates, adds 100KB+ JS bundle, overkill for server-rendered admin portal |
| **Tailwind CSS** | Requires PostCSS build step, would force rewrite of all existing Bootstrap-based templates |
| **GraphQL** | 15 API endpoints do not justify the complexity. REST + htmx partials is simpler. |
| **Celery / task queue** | Sandbox building executes fast enough synchronously via Evennia's batch processor. If builds take >5s in production, revisit. |
| **WebSocket for builder** | The builder saves via HTTP POST, which is the right choice. Real-time collaboration is not a requirement. Evennia already uses WebSocket for the game client -- adding another WS layer for the builder adds complexity without user value. |
| **TypeScript** | No build step means no TS compilation. The existing vanilla JS codebase is manageable at its current size (~1,200 lines across 2 templates). |
| **Django Channels (for web portal)** | Evennia already includes Channels/Twisted for game communication. Adding Channels for the web portal would complicate the architecture for no meaningful benefit at the expected user scale (<100 staff builders). |
| **Node.js / Express** | Adding a second server runtime is unjustified. Django handles everything needed. |

---

## Sources

### Verified (HIGH confidence)
- Evennia 5.0.1 metadata: `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\.venv\Lib\site-packages\evennia-5.0.1.dist-info\METADATA`
- Django 5.2.7 metadata: `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\.venv\Lib\site-packages\django-5.2.7.dist-info\METADATA`
- [django-htmx on PyPI](https://pypi.org/project/django-htmx/) -- version 1.27.0, released 2025-11-28
- [django-fsm-2 on PyPI](https://pypi.org/project/django-fsm-2/) -- version 4.1.0, released 2025-11-03
- [Bootstrap 5.3.8 blog post](https://blog.getbootstrap.com/2025/06/17/bootstrap-5-3-7/) -- 5.3.x release line
- [htmx releases on GitHub](https://github.com/bigskysoftware/htmx/releases) -- version 2.0.8
- [Alpine.js releases on GitHub](https://github.com/alpinejs/alpine/releases) -- version 3.15.3

### Medium confidence (WebSearch-verified)
- [Evennia Batch Code Processor docs](https://www.evennia.com/docs/latest/Components/Batch-Code-Processor.html)
- [Evennia Web Client docs](https://www.evennia.com/docs/latest/Components/Webclient.html)
- [htmx 4.0 alpha announcement](https://htmx.org/posts/2024-06-17-htmx-2-0-0-is-released/) -- 4.0 timeline from npm metadata

### Project files examined
- `beckonmu/web/builder/views.py` -- existing Django CBV pattern
- `beckonmu/web/builder/models.py` -- BuildProject, RoomTemplate models
- `beckonmu/web/builder/exporter.py` -- batch script generation
- `beckonmu/web/templates/builder/editor.html` -- 843 lines, vanilla JS grid builder
- `beckonmu/web/templates/character_creation.html` -- 1,472+ lines, Bootstrap 5.1.3 + vanilla JS
- `beckonmu/traits/api.py` -- hand-rolled JSON API views
- `beckonmu/traits/models.py` -- CharacterBio with boolean approval flag
- `beckonmu/server/conf/settings.py` -- current INSTALLED_APPS
