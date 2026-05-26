---
name: ship-feature
description: Commit, push, create PR, merge, and clean up after a FabricVision feature is complete

allowed-tools: Read, Bash, mcp__github__create_pull_request, mcp__github__merge_pull_request, mcp__github__delete_branch

---

# Step 1 — Identify current branch

Run:

```bash
git branch --show-current
```

Store this as `CURRENT_BRANCH`.

If the current branch is `main`, stop immediately and say:

"You're currently on main. Create and implement a feature branch before running @ship-feature."

---

# Step 2 — Gather release context

Run:

```bash
git diff --staged
git diff
git log main..HEAD --oneline
```

Then locate the matching spec file inside:

```text
.claude/specs/
```

Read the relevant spec to understand:

* feature goal
* architecture boundaries
* testing expectations
* definition of done

Also review:

* `PRD_FabricVision.md`
* `TRD_FabricVision.md`
* `SAD_FabricVision.md`
* `API_FabricVision.md`

to ensure the implementation aligns with:

* async generation architecture
* HTMX interaction rules
* Celery orchestration
* upload handling
* ownership/security boundaries

---

# Step 3 — Generate commit message

Create a Conventional Commit message.

Allowed prefixes:

* `feat:` — new feature
* `fix:` — bug fix
* `refactor:` — internal cleanup without behavior change
* `test:` — tests only
* `docs:` — documentation only
* `chore:` — tooling/config/infra

Rules:

* lowercase only
* no period at the end
* under 72 characters
* describe user-visible capability
* do NOT mention filenames
* do NOT mention implementation details

Good examples:

```text
feat: add virtual try-on upload workflow
feat: enable async generation polling
fix: prevent expired share links from loading
refactor: simplify generation status rendering
```

Bad examples:

```text
feat: updated views.py and celery tasks
fix: changed cloudinary upload logic
```

---

# Step 4 — Commit changes

Run:

```bash
git add .
git commit -m "<generated-message>"
```

Then report:

```text
✓ Committed — <generated-message>
```

If commit fails, stop and report the error.

---

# Step 5 — Push feature branch

Run:

```bash
git push -u origin CURRENT_BRANCH
```

Then report:

```text
✓ Pushed — CURRENT_BRANCH
```

If push fails, stop and report the error.

---

# Step 6 — Create Pull Request

Use GitHub MCP to create a pull request from:

```text
CURRENT_BRANCH → main
```

## PR Title

Use plain English.

Do NOT include conventional commit prefixes.

Example:

```text
Add virtual try-on generation workflow
```

---

## PR Description

Use this structure:

```markdown
## What this PR does

<Short summary derived from the spec overview>

## Architecture Notes

- Async generation handled via Celery only
- HTMX polling integrated for status updates
- Ownership checks enforced for GenerationJob access
- Upload pipeline validated through Cloudinary workflow

## Changes

- apps/... — <summary>
- templates/... — <summary>
- tasks/... — <summary>
- tests/... — <summary>

## Definition of done

<Copy checklist from spec and mark completed items as [x]>

## How to test

1. Start Django server
2. Start Celery worker
3. Upload garment image
4. Submit virtual try-on request
5. Verify polling updates status correctly
6. Confirm generated output renders properly
7. Verify unauthorized users cannot access another GenerationJob
```

After PR creation report:

```text
✓ PR created — <PR URL>
```

If PR creation fails, stop immediately.

---

# Step 7 — Merge Pull Request

Use GitHub MCP to merge the PR using:

```text
Squash Merge
```

After merge report:

```text
✓ PR merged to main
```

If merge fails, stop immediately.

---

# Step 8 — Delete remote feature branch

Use GitHub MCP to delete:

```text
CURRENT_BRANCH
```

Then report:

```text
✓ Remote branch deleted
```

---

# Step 9 — Sync local main

Run:

```bash
git checkout main
git pull origin main
```

Then report:

```text
✓ Switched to main — up to date
```

---

# Step 10 — Delete local feature branch

Run:

```bash
git branch -D CURRENT_BRANCH
```

Then report:

```text
✓ Local branch deleted
```

---

# Final Summary

Print EXACTLY:

```text
────────────────────────────────────────

@ship-feature complete

✓ Committed — <message>
✓ Pushed — <branch>
✓ PR created and merged
✓ Remote branch deleted
✓ Switched to main
✓ Local branch deleted

Next:
- run @test-feature for the next feature
- or run @create-spec to start another workflow

────────────────────────────────────────
```

---

# FabricVision Release Rules

## Never violate async boundaries

A feature must NOT be merged if:

* Replicate calls occur inside Django views
* Long-running generation blocks requests
* Polling bypasses Celery state
* Background orchestration leaks into templates

---

## Ownership protection is mandatory

Before merge verify:

* users can only access their own GenerationJob
* share links respect expiration
* uploads are scoped correctly
* polling endpoints validate ownership

---

## Upload safety rules

Do NOT merge features that:

* allow unrestricted uploads
* skip MIME validation
* expose raw Cloudinary credentials
* trust client-side validation alone

---

## HTMX standards

HTMX interactions must:

* return partials/fragments cleanly
* avoid duplicated rendering logic
* support progressive polling states
* keep templates maintainable

---

## Required preconditions before shipping

Before merge:

* feature spec exists
* implementation completed
* tests written
* code review completed
* critical findings resolved

If any are missing, stop and report:

"Feature is not ready for shipping yet."

---

# Failure Handling

If GitHub MCP is unavailable, stop immediately and say:

```text
GitHub MCP is not connected. Run /mcp to verify integration.
```

If any step fails:

* stop immediately
* report the failure clearly
* do NOT continue to later steps

---

# Final Rule

FabricVision features are only considered complete when:

* async architecture remains clean
* Celery orchestration is preserved
* HTMX workflows remain maintainable
* ownership boundaries are enforced
* uploads remain secure
* tests and reviews are complete

Reliability is more important than shipping speed.
