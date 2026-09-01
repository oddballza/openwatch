# Upstream contribution status

| Ref | Type | Issue | Status |
|---|---|---|---|
| PR #6688 | MT55 coordinator | new device | **MERGED** (commit 8305c4b7b0) |
| PR #6690 | Battery charging (>100 offset) | #5236 | **MERGED** |
| PR #6691 | Sleep-overlay log-spam (WARN->DEBUG) | #5859 | Open, awaiting review |
| Issue #6689 | DND on/off parse bug | - | Open, triaged |
| Issue #5236 comment | Battery charging finding | #5236 | Posted -> became PR #6690 (merged) |

**MT55 is now officially supported in Gadgetbridge** (coordinator merged), and the
battery-while-charging fix (>100 = charging, level-100) is merged too.

All commits authored as oddballza, no AI attribution. PR/issue descriptions carry
the upstream-required "prepared with AI assistance" disclosure + clean-room note.

Out of scope (documented, not submitted): watchface upload (decompilation-derived),
DND on/off *fix* (shared-code semantics, deferred to maintainers via #6689).

Links:
- https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688 (merged)
- https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6690 (merged)
- https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691 (open)
- https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689 (open)
