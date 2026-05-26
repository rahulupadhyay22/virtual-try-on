---
name: code-review-feature
description: Run the FabricVision code review pipeline for a specific spec using security and quality subagents.
---

Run the full FabricVision code review pipeline for the feature specified in $ARGUMENTS.

If no argument is provided, stop immediately and say:

"Please provide a spec name. Usage: /code-review-feature  e.g. /code-review-feature 07-tryon-upload"

If `.claude/specs/$ARGUMENTS.md` does not exist, stop immediately and say:

"Spec file not found at .claude/specs/$ARGUMENTS.md. Please check the spec name and try again."

---

## Pre-flight Check

Before invoking any reviewers:

* Run `git diff` for unstaged changes
* Run `git diff --staged` for staged changes
* Combine both into a single diff

If both diffs are empty, stop immediately and say:

"No changes detected. Implement the feature before running code review."

---

## Step 1: Parallel Review

Invoke BOTH subagents simultaneously with the same context.

DO NOT wait for one reviewer before starting the other.

---

### fabricvision-security-reviewer receives:

* Combined git diff from pre-flight check
* Spec file for context:
  `.claude/specs/$ARGUMENTS.md`
* Architecture references:
  * `PRD_FabricVision.md`
  * `TRD_FabricVision.md`
  * `SAD_FabricVision.md`
  * `API_FabricVision.md`
* Source directories to reference:
  * `apps/`
  * `templates/`
* Instruction:
  Review ONLY the changed code for:
  * authentication issues
  * authorization flaws
  * ownership vulnerabilities
  * upload security
  * HTMX endpoint exposure
  * Celery async boundary violations
  * sensitive data exposure
  * Cloudinary handling risks
  * Replicate API security concerns
  Do NOT comment on:
  * code style
  * maintainability
  * naming
  * architecture cleanliness
  Focus ONLY on security.

---

### fabricvision-quality-reviewer receives:

* Combined git diff from pre-flight check
* Spec file for context:
  `.claude/specs/$ARGUMENTS.md`
* Architecture references:
  * `PRD_FabricVision.md`
  * `TRD_FabricVision.md`
  * `SAD_FabricVision.md`
  * `API_FabricVision.md`
* Source directories to reference:
  * `apps/`
  * `templates/`
* Instruction:
  Review ONLY the changed code for:
  * Django best practices
  * maintainability
  * HTMX workflow quality
  * Celery orchestration quality
  * async boundary consistency
  * ORM/query quality
  * template organization
  * readability
  * separation of concerns
  Do NOT comment on:
  * security vulnerabilities
  * auth flaws
  * secret handling
  Focus ONLY on quality and maintainability.

---

## Step 2: Unified Review Report

After BOTH subagents finish:

Combine both reviews into a single unified report.

De-duplicate overlapping findings.

If both reviewers mention the same code area from different perspectives:

* merge them into a single finding
* include both viewpoints

---

## Final Report Structure

# Code Review Report -- $ARGUMENTS

## Security Findings

[Output from fabricvision-security-reviewer]

---

## Quality Findings

[Output from fabricvision-quality-reviewer]

---

## Combined Action Plan

Create a prioritized checklist:

### Highest Priority

* critical security flaws
* ownership vulnerabilities
* async boundary violations
* sensitive data exposure

### Medium Priority

* maintainability problems
* architectural inconsistencies
* HTMX workflow cleanup
* ORM/query improvements

### Lower Priority

* polish suggestions
* naming improvements
* minor template cleanup
* small refactors

---

## Overall Verdict

One of:

* APPROVED -- ready for commit
* APPROVED WITH SUGGESTIONS -- safe to continue, improvements recommended
* CHANGES REQUIRED -- fix issues before commit

Explain WHY the verdict was chosen.

---

## Step 3: Approval Gate

After presenting the report, ask:

"Do you want me to implement the action plan now?"

Wait for explicit user confirmation before modifying any files.

DO NOT automatically edit code.

---

## Rules

* Do NOT edit files before user approval
* Do NOT skip the git diff pre-flight check
* Do NOT run reviewers sequentially
* Both reviewers MUST run in parallel
* Do NOT review unrelated files
* Do NOT proceed if the spec file does not exist
* If either reviewer fails, report it and stop
* Do NOT present a partial review as complete

---

## FabricVision-Specific Review Priorities

Pay extra attention to:

* GenerationJob ownership enforcement
* credit accounting correctness
* HTMX polling endpoint protection
* Celery async isolation
* prevention of synchronous Replicate calls
* Cloudinary upload validation
* share-link expiration/security
* proper use of Django ORM
* thin views and clean task orchestration
* template fragment maintainability

---

## Final Rule

A feature is NOT production-ready if it:

* breaks async architecture boundaries
* exposes another user's GenerationJob
* leaks secrets/tokens
* allows unsafe uploads
* tightly couples AI orchestration into views
* creates unmaintainable HTMX workflows

FabricVision reliability depends on preserving these boundaries.
