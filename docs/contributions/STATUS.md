# Upstream contribution status — ALL MERGED

| Ref | Type | Issue | Status |
|---|---|---|---|
| PR #6688 | MT55 coordinator | new device | **MERGED** |
| PR #6690 | Battery charging (>100 = charging, level-100) | #5236 | **MERGED** |
| PR #6691 | Sleep-overlay log-spam (WARN->DEBUG) | #5859 | **MERGED** |
| Issue #6689 | DND on/off parse bug | - | Open (documented for maintainers) |
| Issue #5236 comment | Battery charging finding | #5236 | Posted -> became merged PR #6690 |

**MT55 is officially supported in Gadgetbridge.** Two shared-code fixes benefiting
all Moyoung watches were also merged (battery-while-charging, log-spam). Referenced
issues left open intentionally ("Addresses", not "Fixes") since each has aspects
beyond our changes.

All commits authored as oddballza, no AI attribution; PR/issue text carried the
upstream-required AI disclosure + clean-room statement.

Out of scope (documented, not submitted): watchface upload (decompilation-derived,
private-use only); DND on/off *fix* (shared-code semantics deferred via #6689).
