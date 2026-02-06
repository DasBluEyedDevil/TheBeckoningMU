# Phase 2: Character Approval Completion - Research

**Researched:** 2026-02-03
**Domain:** Evennia character lifecycle management, Django model extensions, web-based chargen workflow
**Confidence:** HIGH

## Summary

Phase 2 completes the character creation lifecycle that is partially built. The existing system allows players to create characters via a web form (character_creation.html) and staff to review/approve/reject them via both a web interface (character_approval.html) and in-game commands (+pending, +review, +approve, +reject). However, five capabilities are missing: (1) rejected characters have no way to be edited and resubmitted through the web UI, (2) CharacterBio has no background/backstory text field, (3) approved characters are not auto-placed in a starting room, (4) notifications only work if the player is online when staff acts, and (5) there is no draft save/resume functionality.

The existing codebase is well-structured for extension. The CharacterBio model (in `beckonmu/traits/models.py`) needs a `status` field to replace the simple `approved` boolean, a `background` text field, and `rejection_notes`/`rejection_count` fields. The CharacterApprovalAPI (in `beckonmu/traits/api.py`) needs to handle rejection notes storage and resubmission logic. The character_creation.html frontend needs to detect whether it is creating a new character or editing a rejected one, and the character_approval.html needs a proper rejection notes textarea (currently uses `window.prompt()`). For notifications, the codebase already uses `account.msg()` for online players (see chargen.py lines 461-471, 576-584); for offline players, Evennia's persistent `Msg` system or `account.db` attributes should store pending notifications that deliver on login. For auto-placement, `character.move_to()` with the configured `START_LOCATION` (default `#2`, Limbo) is the Evennia pattern.

**Primary recommendation:** Extend CharacterBio with status/background/rejection fields via Django migration, add resubmission API endpoint, modify the web frontend to support edit mode for rejected characters, implement notification storage on account.db for offline delivery, and auto-place approved characters using Evennia's move_to().

## Standard Stack

This phase does NOT add new libraries. It extends existing code using the current stack.

### Core (Already Installed)
| Library | Version | Purpose | Role in Phase 2 |
|---------|---------|---------|-----------------|
| Django | 5.2.7 | Web framework | Model migrations, views, URL routing |
| Evennia | 5.0.1 | MUD framework | `move_to()`, `msg()`, `create_message()`, START_LOCATION |
| Bootstrap | 5.1.3 | CSS framework | UI for rejection notes, background field, notification display |
| Vanilla JS | ES6+ | Frontend | Form state management, draft save via localStorage |

### Supporting (No New Installs)
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `evennia.create_message` | Persistent Msg for offline notifications | Approval/rejection notification storage |
| `evennia.utils.search.search_tag` | Find the starting room | Auto-placement on approval |
| `django.db.migrations` | Add fields to CharacterBio | Status, background, rejection_notes fields |
| `localStorage` (browser) | Client-side draft persistence | Draft save/resume for character creation |

### Why NOT django-fsm-2 Yet
Prior research (STACK.md) recommends django-fsm-2 for approval state machines. However, for Phase 2, the character approval workflow has only 4 states (draft, submitted, rejected, approved) with simple transitions. A CharField with choices + explicit transition validation in the view layer is sufficient and avoids adding a dependency for a simple state machine. django-fsm-2 becomes valuable in Phase 3+ when the builder project lifecycle has 5+ states. This keeps Phase 2 lean.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CharField status | django-fsm-2 FSMField | FSM is overkill for 4-state linear workflow; adds dependency |
| localStorage for drafts | Server-side draft model | Server drafts require API endpoint + DB storage; localStorage is simpler for MVP |
| account.db notifications | Evennia Msg system | Msg system requires custom reading UI; account.db + at_post_login is simpler and matches existing patterns |
| window.prompt() for reject | Proper textarea in modal | Modal is better UX and already how other MU* web tools work |

**Installation:** None needed. All tools are already in the stack.

## Architecture Patterns

### Existing Project Structure (Files to Modify)
```
beckonmu/
  traits/
    models.py           # ADD: status, background, rejection_notes, rejection_count to CharacterBio
    api.py              # MODIFY: CharacterApprovalAPI (rejection notes), CharacterCreateAPI (resubmit)
                        # ADD: CharacterResubmitAPI, CharacterDraftAPI, MyCharactersAPI
    urls.py             # ADD: new endpoint routes
    utils.py            # MODIFY: enhanced_import_character_from_json (handle resubmission)
    migrations/         # ADD: 0002_characterbio_status_background.py
  commands/
    chargen.py          # MODIFY: CmdApprove (auto-place), CmdReject (store notes on model)
  typeclasses/
    characters.py       # MODIFY: at_post_puppet or at_object_creation (notification delivery)
  web/
    website/
      views/__init__.py # MODIFY: CharacterCreationView (pass character data for edit mode)
    templates/
      character_creation.html  # MODIFY: edit mode for rejected chars, background field, draft save
      character_approval.html  # MODIFY: rejection notes textarea (replace prompt())
```

### Pattern 1: CharacterBio Status Field (Replacing Boolean)
**What:** Replace `approved = BooleanField` with `status = CharField(choices=...)` to track the full character lifecycle.
**When to use:** All places that currently check `bio.approved`.
**Example:**
```python
# Source: Existing CharacterBio model in traits/models.py

class CharacterBio(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),           # Player started but hasn't submitted
        ('submitted', 'Submitted'),   # Player submitted for review
        ('rejected', 'Rejected'),     # Staff rejected, awaiting player revision
        ('approved', 'Approved'),     # Staff approved, ready for play
    ]

    # Replace: approved = BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current approval status"
    )

    # NEW FIELDS:
    background = models.TextField(
        blank=True,
        help_text="Character's backstory/background narrative"
    )
    rejection_notes = models.TextField(
        blank=True,
        help_text="Staff feedback on why character was rejected"
    )
    rejection_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this character has been rejected"
    )

    # KEEP existing approved_by, approved_at fields for audit trail
    # KEEP: approved property for backwards compatibility
    @property
    def approved(self):
        return self.status == 'approved'
```

### Pattern 2: Backward-Compatible Migration
**What:** Add new fields alongside the existing `approved` boolean, then add a data migration to convert existing data, then remove the old field.
**When to use:** When changing an existing model field that is referenced in multiple files.
**Example:**
```python
# Migration step 1: Add new fields, keep old field
# - Add status CharField with default='draft'
# - Add background, rejection_notes, rejection_count
# - Data migration: if approved=True -> status='approved', else status='submitted'

# Migration step 2 (can be same migration):
# - Remove old approved BooleanField
# - Add @property approved for backwards compat
```

### Pattern 3: Resubmission Flow
**What:** When a character is rejected, the player can load the existing data into the character creation form, edit it, and resubmit. The resubmission clears rejection notes and sets status back to 'submitted'.
**When to use:** Rejected character editing.
**Example:**
```python
# API endpoint: GET /api/traits/character/<id>/for-edit/
# Returns: full character data in the same format as creation form expects
# Auth: must be the character's owner

# API endpoint: POST /api/traits/character/<id>/resubmit/
# Accepts: updated character_data (same format as create)
# Auth: must be the character's owner, character must be in 'rejected' status
# Effect: updates traits, bio, background; sets status='submitted'
```

### Pattern 4: Notification Storage on Account
**What:** Store pending notifications as a list on `account.db.pending_notifications`. Deliver them in `at_post_login()` or when the account first connects a session.
**When to use:** Any time a notification needs to reach a player who may be offline.
**Example:**
```python
# Source: Evennia pattern for persistent notifications

# Storing a notification (in CharacterApprovalAPI or CmdApprove):
def notify_account(account, message, notification_type="info"):
    """Store a notification for delivery on next login."""
    if not account.db.pending_notifications:
        account.db.pending_notifications = []
    account.db.pending_notifications.append({
        'message': message,
        'type': notification_type,
        'timestamp': timezone.now().isoformat(),
        'read': False,
    })
    # Also try immediate delivery if online
    if account.sessions.count():
        account.msg(message)

# Delivering on login (in typeclasses/accounts.py or via at_post_login hook):
def at_post_login(self, session=None, **kwargs):
    super().at_post_login(session=session, **kwargs)
    pending = self.db.pending_notifications or []
    if pending:
        for notif in pending:
            if not notif.get('read'):
                self.msg(notif['message'])
                notif['read'] = True
        # Clear delivered notifications
        self.db.pending_notifications = [n for n in pending if not n.get('read')]
```

### Pattern 5: Auto-Placement on Approval
**What:** When a character is approved, set their location and home to the game's starting room.
**When to use:** In both the web API (`CharacterApprovalAPI.post()`) and the in-game command (`CmdApprove`).
**Example:**
```python
# Source: Evennia documentation for object movement

from django.conf import settings
from evennia.objects.models import ObjectDB

def place_approved_character(character):
    """Move an approved character to the starting room."""
    # Get START_LOCATION from settings (default: #2, Limbo)
    start_location_dbref = getattr(settings, 'START_LOCATION', '#2')

    # Find the room
    try:
        # Parse the dbref string to get the ID
        room_id = int(start_location_dbref.strip('#'))
        start_room = ObjectDB.objects.get(id=room_id)
    except (ValueError, ObjectDB.DoesNotExist):
        # Fallback to Limbo (#2)
        start_room = ObjectDB.objects.get(id=2)

    # Set home and move character
    character.home = start_room
    character.move_to(start_room, quiet=True)
    character.save()
```

### Pattern 6: Draft Save via localStorage
**What:** Periodically save form state to browser localStorage. On page load, check for saved draft and offer to resume.
**When to use:** Character creation form (character_creation.html).
**Example:**
```javascript
// Save draft every 30 seconds and on field change
function saveDraft() {
    const draft = {
        full_name: document.getElementById('full_name').value,
        concept: document.getElementById('concept').value,
        clan: document.getElementById('clan').value,
        // ... all form fields
        traitValues: { ...traitValues },
        disciplineValues: { ...disciplineValues },
        advantageValues: { ...advantageValues },
        flawValues: { ...flawValues },
        attributePriorities: { ...attributePriorities },
        skillPriorities: { ...skillPriorities },
        savedAt: new Date().toISOString(),
    };
    localStorage.setItem('chargen_draft', JSON.stringify(draft));
}

function loadDraft() {
    const saved = localStorage.getItem('chargen_draft');
    if (saved) {
        const draft = JSON.parse(saved);
        const savedDate = new Date(draft.savedAt);
        if (confirm(`Resume draft from ${savedDate.toLocaleString()}?`)) {
            applyDraftToForm(draft);
        } else {
            localStorage.removeItem('chargen_draft');
        }
    }
}

// Clear draft on successful submission
function clearDraft() {
    localStorage.removeItem('chargen_draft');
}
```

### Anti-Patterns to Avoid
- **Deleting the character object on rejection:** The existing system creates the character with `location=None` on submission. On rejection, do NOT delete and recreate -- just update the existing object's traits. This preserves the character ID, any staff edit logs, and the Jobs system link.
- **Using session storage for drafts:** Django sessions expire. localStorage persists across browser sessions and does not consume server resources. For an MVP, localStorage is the right choice.
- **Sending notifications via Evennia Msg for character approval:** The Msg system is designed for in-game mail/page. It has no built-in UI for reading. Using `account.db.pending_notifications` is simpler and integrates with the existing `account.msg()` pattern already used in chargen.py.
- **Adding a separate CharacterApplication model:** The existing CharacterBio already tracks per-character approval state. Adding another model creates data synchronization issues. Extend CharacterBio instead.
- **Trying to validate priority distribution (7/5/3) on resubmission:** Phase 1 research confirmed that validating which category gets which priority is hard to reverse-engineer from flat trait data. Validate totals only (matching existing `validate_v5_chargen_pools`). Staff review catches priority issues.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Character placement in room | Custom room lookup | `settings.START_LOCATION` + `ObjectDB.objects.get(id=...)` + `character.move_to()` | Evennia's built-in pattern; handles all the edge cases |
| Notification to offline players | Custom notification model with read/unread tracking | `account.db.pending_notifications` list + `at_post_login` delivery | Matches existing pattern in chargen.py; avoids new DB model |
| Form state persistence | Server-side draft endpoint with partial validation | `localStorage.setItem/getItem` | Zero server cost; works offline; browser handles cleanup |
| Character data re-population on edit | Custom serialization format | Re-use existing `export_character_to_json()` from `traits/utils.py` | Already exists and produces the right format |
| CSRF token handling in new endpoints | Manual token extraction | Django's built-in CsrfViewMiddleware (Phase 1 already fixed this) | All @csrf_exempt removed in Phase 1; new endpoints get CSRF for free |

**Key insight:** The existing codebase has most of the building blocks. The character creation form already sends data in the right format. The approval API already handles approve/reject. The export function already serializes character data. Phase 2 connects these pieces and fills the gaps.

## Common Pitfalls

### Pitfall 1: Backward Compatibility with `approved` Boolean
**What goes wrong:** Existing code references `bio.approved` as a boolean in multiple places (chargen.py, api.py, templates). Replacing it with a status CharField breaks all those references.
**Why it happens:** Field replacement without checking all call sites.
**How to avoid:** Add the `status` field as new. Add an `@property approved` that returns `self.status == 'approved'`. Update the setter in `CharacterApprovalAPI` to set `bio.status = 'approved'` instead of `bio.approved = True`. Keep the old field through one migration cycle, then remove it. Places that check `bio.approved` (at least 8 locations): `PendingCharactersAPI.get()`, `CharacterApprovalAPI.post()`, `CharacterDetailAPI.get()`, `CmdPending.func()`, `CmdReview.func()`, `CmdApprove.func()`, `enhanced_import_character_from_json()`, `character_approval.html`.
**Warning signs:** FieldError or AttributeError on `approved` after migration.

### Pitfall 2: Resubmission Deletes vs Updates Traits
**What goes wrong:** On resubmission, calling `enhanced_import_character_from_json()` again creates duplicate CharacterTrait rows instead of updating existing ones.
**Why it happens:** `CharacterTrait` has `unique_together = ['character', 'trait', 'instance_name', 'specialty']`. The import uses `get_or_create`. If the trait already exists with the same key, it updates (good). But if the player changes an instanced trait's name, it creates a new row and the old one remains.
**How to avoid:** Before resubmission import, delete ALL existing CharacterTrait and CharacterPower rows for the character, then re-import fresh. This is simpler than diff-and-patch and guarantees consistency. The data loss is acceptable because the player is resubmitting with complete data.
**Warning signs:** Characters with duplicate traits after resubmission.

### Pitfall 3: Auto-Placement Race Condition with Web API
**What goes wrong:** `CharacterApprovalAPI.post()` calls `character.move_to()` from a Django web request. But Evennia's `move_to()` triggers hooks (`at_pre_move`, `announce_move_to`, `at_post_move`) that may try to message characters in the room. If the game server's object cache is out of sync with the web process, this can cause errors.
**Why it happens:** Phase 1 research noted that `create.create_object()` from a web view may not sync with Evennia's idmapper cache (Pitfall 2 in Phase 1 research).
**How to avoid:** For auto-placement via the web API, use `quiet=True` on `move_to()` to suppress room announcements. Alternatively, defer placement: set a flag on the character (`character.db.needs_placement = True`) and let a game-side script or `at_post_puppet` handle the actual move. For the in-game `+approve` command, `move_to()` works directly because it runs in the game server process.
**Warning signs:** Error traces mentioning idmapper or "object not found" when approving via web.

### Pitfall 4: localStorage Draft Overwrites Server-Side Rejected Character
**What goes wrong:** Player starts a new character, saves draft to localStorage. Then their previous character gets rejected. Player opens character creation page -- the localStorage draft (for the new character) overwrites the rejected character's edit form.
**How to avoid:** Key localStorage drafts by character name or ID: `chargen_draft_${characterId}` for resubmissions, `chargen_draft_new` for new characters. The edit mode URL should include the character ID so the frontend knows which draft to load.
**Warning signs:** Player edits wrong character's data.

### Pitfall 5: Rejection Notes Not Visible on Web
**What goes wrong:** Staff rejects via the in-game `+reject` command, which stores rejection reason in `character.db.staff_actions`. But the web UI has no way to read Evennia `db` attributes (they are not Django model fields -- they use Evennia's custom Attribute system stored in a separate table).
**Why it happens:** The existing rejection flow stores notes in `character.db.staff_actions` (Evennia attributes), not in the CharacterBio model (Django field).
**How to avoid:** Store rejection notes in BOTH places: the CharacterBio.rejection_notes field (accessible via Django ORM in web views) AND character.db.staff_actions (accessible in-game). The web API should read from CharacterBio.rejection_notes. The in-game +reject command should write to both.
**Warning signs:** Player sees "Your character was rejected" but cannot see why on the web.

### Pitfall 6: Comment Model Field Name Mismatch
**What goes wrong:** In chargen.py line 502, `Comment.objects.create(job=job, author=..., text=comment_text)` uses field name `text`. But the Comment model in jobs/models.py defines the field as `content`, not `text`.
**Why it happens:** This is a pre-existing bug that would cause a TypeError when the Jobs integration runs.
**How to avoid:** When modifying chargen.py, verify the Comment model field name. Use `content=comment_text` instead of `text=comment_text`.
**Warning signs:** TypeError on `+approve` or `+reject` when Jobs integration tries to create comments.

## Code Examples

### Example 1: CharacterBio Model Extension
```python
# Source: Existing beckonmu/traits/models.py CharacterBio class

class CharacterBio(models.Model):
    """Stores character background information specific to VtM 5e."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]

    character = models.OneToOneField(ObjectDB, on_delete=models.CASCADE, related_name='vtm_bio')

    # Existing fields (keep all)
    full_name = models.CharField(max_length=200, blank=True)
    concept = models.CharField(max_length=100, blank=True)
    ambition = models.TextField(blank=True)
    desire = models.TextField(blank=True)
    clan = models.CharField(max_length=50, blank=True)
    sire = models.CharField(max_length=100, blank=True)
    generation = models.PositiveSmallIntegerField(blank=True, null=True)
    predator_type = models.CharField(max_length=50, blank=True)
    splat = models.CharField(max_length=20, default='mortal')

    # NEW: Replace boolean with status field
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current approval status"
    )

    # NEW: Background/backstory field (CHAR-02)
    background = models.TextField(
        blank=True,
        help_text="Character's backstory/background narrative"
    )

    # NEW: Rejection tracking (CHAR-01)
    rejection_notes = models.TextField(
        blank=True,
        help_text="Staff feedback on why character was rejected"
    )
    rejection_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this character has been rejected"
    )

    # KEEP existing approval audit fields
    approved_by = models.CharField(max_length=100, blank=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def approved(self):
        """Backward compatibility: returns True if status is 'approved'."""
        return self.status == 'approved'
```

### Example 2: Approval API with Auto-Placement and Notifications
```python
# Source: Existing CharacterApprovalAPI in beckonmu/traits/api.py

class CharacterApprovalAPI(BaseAPIView):
    def post(self, request, character_id):
        # ... existing auth/validation ...

        if action == 'approve':
            # Idempotent check
            if bio.status == 'approved':
                return JsonResponse({'error': 'Already approved'}, status=409)

            bio.status = 'approved'
            bio.approved_by = request.user.username
            bio.approved_at = timezone.now()
            bio.save()

            # CHAR-03: Auto-place character in starting room
            place_approved_character(character)

            # CHAR-04: Notify player
            notify_account(
                character.db_account,
                f"Your character '{character.db_key}' has been APPROVED! "
                f"You may now log in and play.",
                notification_type="approval"
            )

        elif action == 'reject':
            bio.status = 'rejected'
            bio.rejection_notes = notes  # from request.json.get('notes', '')
            bio.rejection_count += 1
            bio.approved_by = request.user.username  # who reviewed
            bio.approved_at = timezone.now()  # when reviewed
            bio.save()

            # Also store in Evennia attributes for in-game access
            if notes:
                character.db.approval_notes = notes

            # CHAR-04: Notify player of rejection with notes
            notify_account(
                character.db_account,
                f"Your character '{character.db_key}' requires revisions.\n"
                f"Staff feedback: {notes}\n"
                f"Please edit and resubmit via the character creation page.",
                notification_type="rejection"
            )
```

### Example 3: My Characters API (for player to see their characters and status)
```python
# NEW endpoint: GET /api/traits/my-characters/
class MyCharactersAPI(BaseAPIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Get all characters owned by this account
        from evennia.objects.models import ObjectDB
        characters = ObjectDB.objects.filter(
            db_account=request.user,
            db_typeclass_path__contains='characters'
        )

        data = []
        for char in characters:
            try:
                bio = CharacterBio.objects.get(character=char)
                data.append({
                    'character_id': char.id,
                    'character_name': char.db_key,
                    'status': bio.status,
                    'clan': bio.clan,
                    'concept': bio.concept,
                    'rejection_notes': bio.rejection_notes if bio.status == 'rejected' else '',
                    'rejection_count': bio.rejection_count,
                    'created_at': bio.created_at.isoformat(),
                    'updated_at': bio.updated_at.isoformat(),
                })
            except CharacterBio.DoesNotExist:
                pass

        return JsonResponse({'characters': data})
```

### Example 4: Character Edit Data API (for resubmission)
```python
# NEW endpoint: GET /api/traits/character/<id>/for-edit/
class CharacterEditDataAPI(BaseAPIView):
    def get(self, request, character_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            character = ObjectDB.objects.get(id=character_id)
        except ObjectDB.DoesNotExist:
            return JsonResponse({'error': 'Character not found'}, status=404)

        # Must be the character's owner
        if character.db_account != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Must be in rejected status
        try:
            bio = CharacterBio.objects.get(character=character)
        except CharacterBio.DoesNotExist:
            return JsonResponse({'error': 'Character bio not found'}, status=404)

        if bio.status != 'rejected':
            return JsonResponse({'error': 'Only rejected characters can be edited'}, status=400)

        # Use existing export function to get character data
        from .utils import export_character_to_json
        character_data = export_character_to_json(character, include_powers=True)

        # Add bio fields that export doesn't include
        character_data['background'] = bio.background
        character_data['ambition'] = bio.ambition
        character_data['desire'] = bio.desire
        character_data['sire'] = bio.sire
        character_data['generation'] = bio.generation
        character_data['predator_type'] = bio.predator_type

        return JsonResponse({
            'character_id': character.id,
            'character_data': character_data,
            'rejection_notes': bio.rejection_notes,
            'rejection_count': bio.rejection_count,
        })
```

### Example 5: Resubmission API
```python
# NEW endpoint: POST /api/traits/character/<id>/resubmit/
class CharacterResubmitAPI(BaseAPIView):
    def post(self, request, character_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            character = ObjectDB.objects.get(id=character_id)
        except ObjectDB.DoesNotExist:
            return JsonResponse({'error': 'Character not found'}, status=404)

        if character.db_account != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        bio = CharacterBio.objects.get(character=character)
        if bio.status != 'rejected':
            return JsonResponse({'error': 'Only rejected characters can be resubmitted'}, status=400)

        character_data = request.json.get('character_data')
        if not character_data:
            return JsonResponse({'error': 'Missing character_data'}, status=400)

        # Clear existing traits before re-import
        CharacterTrait.objects.filter(character=character).delete()
        CharacterPower.objects.filter(character=character).delete()

        # Re-import traits
        results = enhanced_import_character_from_json(character, character_data)
        if not results['success']:
            return JsonResponse({'error': 'Validation failed', 'errors': results['errors'] + results['validation_errors']}, status=400)

        # Update bio fields
        bio.full_name = character_data.get('name', bio.full_name)
        bio.concept = character_data.get('concept', bio.concept)
        bio.clan = character_data.get('clan', bio.clan)
        bio.sire = character_data.get('sire', bio.sire)
        bio.generation = character_data.get('generation', bio.generation)
        bio.predator_type = character_data.get('predator_type', bio.predator_type)
        bio.ambition = character_data.get('ambition', bio.ambition)
        bio.desire = character_data.get('desire', bio.desire)
        bio.background = character_data.get('background', bio.background)
        bio.status = 'submitted'
        bio.rejection_notes = ''  # Clear old rejection notes
        bio.save()

        return JsonResponse({
            'success': True,
            'character_id': character.id,
            'message': 'Character resubmitted for approval'
        })
```

## Existing Code Inventory (What Exists vs What's Missing)

### What Already Works
| Feature | Location | Status |
|---------|----------|--------|
| Character creation web form | `character_creation.html` | Working -- submits to /api/traits/character/create/ |
| Character data import | `traits/utils.py` `enhanced_import_character_from_json()` | Working -- validates V5 rules, imports traits |
| Character data export | `traits/utils.py` `export_character_to_json()` | Working -- serializes character to JSON |
| Staff approval web UI | `character_approval.html` | Working -- lists pending, shows sheet, approve/reject buttons |
| Staff approval API | `traits/api.py` `CharacterApprovalAPI` | Working -- accepts approve/reject with notes |
| In-game +pending, +review | `commands/chargen.py` | Working -- lists/displays pending characters |
| In-game +approve, +reject | `commands/chargen.py` | Working -- sets bio.approved, sends msg to online player |
| Jobs integration | `commands/chargen.py` | Partial -- creates comments on approve/reject (but uses wrong field name `text` instead of `content`) |
| Auth checks on all API endpoints | `traits/api.py` | Fixed in Phase 1 |
| CSRF protection | All endpoints | Fixed in Phase 1 |
| Server-side V5 validation | `traits/utils.py` `validate_v5_chargen_pools()` | Fixed in Phase 1 |

### What's Missing (Phase 2 Requirements)
| Requirement | What Needs to Change | Complexity |
|-------------|---------------------|------------|
| CHAR-01: Rejection resubmission | Add status field, resubmit API, edit mode in frontend | MEDIUM |
| CHAR-02: Background text field | Add field to CharacterBio + model, add to creation form + approval display | LOW |
| CHAR-03: Auto-placement on approval | Add move_to() call in approval API + +approve command | LOW |
| CHAR-04: Offline notifications | Add account.db.pending_notifications + at_post_login delivery | LOW |
| CHAR-05: Draft save/resume | Add localStorage persistence in frontend JS | MEDIUM |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `approved = BooleanField` | `status = CharField(choices=...)` | Phase 2 (this phase) | Enables draft/submitted/rejected/approved states |
| No rejection feedback | `rejection_notes` field + web display | Phase 2 (this phase) | Players can see why they were rejected |
| No background field | `background = TextField` on CharacterBio | Phase 2 (this phase) | Players can write a backstory |
| Approved chars stuck at location=None | Auto-place via `move_to(START_LOCATION)` | Phase 2 (this phase) | Approved characters can immediately play |
| Notifications only for online players | `account.db.pending_notifications` + `at_post_login` | Phase 2 (this phase) | Offline players see notifications on login |
| All-or-nothing character creation | localStorage draft save + resume prompt | Phase 2 (this phase) | Players can save and continue later |
| window.prompt() for rejection notes | Textarea in a modal dialog | Phase 2 (this phase) | Better UX for staff |

## Open Questions

1. **Should draft save also work server-side?**
   - What we know: localStorage is client-side only. If the player clears browser data or uses a different device, the draft is lost.
   - What's unclear: Is device portability important for this user base?
   - Recommendation: Start with localStorage (CHAR-05 MVP). If players request server-side drafts, add a `draft_data` JSONField to CharacterBio in a future phase.

2. **What room should be START_LOCATION?**
   - What we know: The default is `#2` (Limbo). The game may have a custom starting room.
   - What's unclear: Has the admin set up a proper starting room? Is there an OOC area vs IC area distinction?
   - Recommendation: Use `settings.START_LOCATION` (reads from settings.py). If not set, fall back to `#2`. The admin can configure this without code changes.

3. **Should the character name be editable on resubmission?**
   - What we know: The character name is both the `CharacterBio.full_name` and the Evennia `ObjectDB.db_key`. Changing `db_key` affects in-game lookups.
   - What's unclear: If staff rejects because the name is inappropriate, should the player be able to change it?
   - Recommendation: Allow name changes on resubmission. Update both `bio.full_name` and `character.db_key`. Add a check that the new name doesn't conflict with existing characters.

4. **How should the web UI route between new character creation and editing a rejected one?**
   - What we know: Currently `/character-creation/` always shows a blank form.
   - What's unclear: Should rejected character editing be a separate URL or the same URL with a query parameter?
   - Recommendation: Use `/character-creation/?edit=<character_id>` for editing. The template view passes the character ID to JavaScript, which fetches the character data from the for-edit API endpoint. If no `edit` parameter, show blank form.

## Sources

### Primary (HIGH confidence)
- Direct source code analysis of `beckonmu/traits/models.py` (376 lines) -- CharacterBio model, all fields examined
- Direct source code analysis of `beckonmu/traits/api.py` (564 lines) -- all 11 API views including CharacterApprovalAPI
- Direct source code analysis of `beckonmu/traits/utils.py` (753 lines) -- import/export/validation functions
- Direct source code analysis of `beckonmu/commands/chargen.py` (775 lines) -- all staff approval commands
- Direct source code analysis of `beckonmu/web/templates/character_creation.html` (1,471 lines) -- form structure and JS
- Direct source code analysis of `beckonmu/web/templates/character_approval.html` (430 lines) -- staff UI
- Direct source code analysis of `beckonmu/web/website/views/__init__.py` (35 lines) -- template views
- Direct source code analysis of `beckonmu/traits/urls.py` (39 lines) -- all API routes
- Phase 1 Research (`.planning/phases/01-review-and-hardening/01-RESEARCH.md`) -- security fixes, existing patterns
- Prior research (`.planning/research/STACK.md`) -- django-fsm-2 recommendation, htmx patterns

### Secondary (MEDIUM confidence)
- [Evennia Msg documentation](https://www.evennia.com/docs/latest/Components/Msg.html) -- persistent message system
- [Evennia character creation tutorial](https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part3/Beginner-Tutorial-Chargen.html) -- chargen patterns
- [Evennia default settings](https://www.evennia.com/docs/latest/Setup/Settings-Default.html) -- START_LOCATION, DEFAULT_HOME
- [Evennia accounts API](https://www.evennia.com/docs/latest/api/evennia.accounts.accounts.html) -- account.msg() behavior

### Tertiary (LOW confidence)
- WebSearch for "Evennia notification to offline player" -- confirmed account.db pattern is standard community approach
- Prior research (`.planning/research/FEATURES.md`) -- draft save/resume was flagged as needing session management research

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries needed; all extensions use existing Django/Evennia patterns
- Architecture patterns: HIGH -- all patterns verified against existing codebase; resubmission flow uses existing export_character_to_json()
- Model changes: HIGH -- CharacterBio extension is straightforward Django model change with migration
- Auto-placement: HIGH -- Evennia move_to() and START_LOCATION are well-documented
- Notifications: MEDIUM -- account.db.pending_notifications is a community pattern, not official Evennia documentation
- Draft save/resume: MEDIUM -- localStorage approach is standard web practice but not verified against this specific form's complexity
- Pitfalls: HIGH -- all pitfalls identified through direct code reading of call sites and data flow

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (stable codebase, no fast-moving dependencies)
