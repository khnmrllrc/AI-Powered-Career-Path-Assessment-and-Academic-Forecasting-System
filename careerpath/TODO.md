# TODO - CSRF 403 Fix

- [ ] Add `@csrf_protect` to `toggle_assessment_test_status` view (and import `csrf_protect`).
- [ ] Re-run the POST that triggers `/counselor/assessment-tests/<id>/toggle/` to confirm CSRF passes.
- [ ] If still failing: locate any JS/fetch POSTs that might be missing CSRF headers.
- [ ] If still failing: confirm cookies are accepted and no cross-site iframe is involved.

