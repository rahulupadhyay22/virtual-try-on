Run the full FabricVision testing pipeline for the feature specified in $ARGUMENTS.

If no argument is provided, stop immediately and say:

"Please provide a spec name. Usage: @test-feature  e.g. /test-feature 07-tryon-upload"

If `.claude/specs/$ARGUMENTS.md` does not exist, stop immediately and say:

"Spec file not found at .claude/specs/$ARGUMENTS.md. Please check the spec name and try again."


## Step 1: Write Tests

Invoke the **fabricvision-test-writer** subagent with the following context:

* Spec file to base tests on:
  `.claude/specs/$ARGUMENTS.md`

* Architecture and contract references:

  * `PRD_FabricVision.md`
  * `TRD_FabricVision.md`
  * `SAD_FabricVision.md`
  * `API_FabricVision.md`

* Source directories to read for structure only:

  * `apps/`
  * `templates/`

* Output test files to create under:
  `tests/`

* Instruction:

  Write Django tests based on what the specification says the feature SHOULD do.

  Do NOT derive expected behavior from implementation details.

  Cover:

  * happy paths
  * authentication and authorization
  * HTMX behavior
  * Celery workflows
  * ownership rules
  * validation errors
  * database side effects
  * edge cases
  * async status transitions

  Ensure:

  * external APIs are mocked
  * Cloudinary uploads are mocked
  * Replicate API calls are mocked
  * Celery tasks remain asynchronous
  * tests are deterministic and isolated

Wait for `fabricvision-test-writer` to fully complete and confirm the test files have been written before proceeding to Step 2.

---

## Step 2: Run Tests

Once `fabricvision-test-writer` has finished, invoke the **fabricvision-test-runner** subagent with the following context:

* Test files to execute:
  `tests/`

* Spec file for context:
  `.claude/specs/$ARGUMENTS.md`

* Architecture references:

  * `PRD_FabricVision.md`
  * `TRD_FabricVision.md`
  * `SAD_FabricVision.md`
  * `API_FabricVision.md`

* Source directories to analyze against when diagnosing failures:

  * `apps/`
  * `templates/`

* Preferred run commands:

  * `python manage.py test`
  * `pytest`

* Instruction:

  Run ONLY the tests related to the specified feature.

  Do NOT run unrelated test suites.

  Analyze failures by cross-referencing:

  * the specification
  * the generated tests
  * the architecture documents
  * the relevant source files

  Validate:

  * HTMX fragment behavior
  * Celery task dispatch
  * ownership protections
  * permission enforcement
  * database consistency
  * async workflow correctness

  Classify each failure as one of:

  * implementation bug
  * missing feature
  * invalid test expectation
  * architecture violation

---

## Handoff Rules

* Do NOT start Step 2 until Step 1 is fully complete
* Do NOT silently remove assertions to force passing tests
* Do NOT bypass architecture constraints
* Do NOT allow real external API calls
* Do NOT run unrelated test suites
* If `fabricvision-test-writer` reports it could not write the test files, stop immediately and report the reason
* Preserve async boundaries at all times

---

## Final Output

After both subagents complete, produce a combined summary:

### Testing Pipeline Report — $ARGUMENTS

**Step 1 — Tests Written**

* List each generated test file
* List each major test case written
* Include a one-line description of which specification requirement each test validates

**Step 2 — Test Results**

* Mirror the `fabricvision-test-runner` structured report
* Include executed commands
* Include failing tests if any
* Include root-cause analysis for failures

**Verdict**

One of:

* ✅ Ready for code review — all tests pass
* ❌ Needs fixes — list failing tests and root causes
