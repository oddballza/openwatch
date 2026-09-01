# FILED as PR #6691 — Fix: Moyoung sleep-overlay log spam (addresses #5859)

https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691

Branch: `fix-moyoung-sleep-log-spam` (local, based on upstream master ac67e98).
NOT pushed to Codeberg — awaiting owner go-ahead.

## Root cause
`MoyoungActivitySampleProvider.getGBActivitySamples()` calls `overlaySleep()` on
every activity-sample fetch (charts/dashboard). When the queried range has <2
sleep-stage samples — a normal condition (daytime ranges, days without recorded
sleep) — it logs at WARN and returns. Every chart refresh over such a range emits
a warning.

## Reproduced on MT55 (clean-room)
Navigating GB charts/dashboard for ~2 minutes produced **208** occurrences of
"Not overlaying sleep data ...". Matches the reporter's 4,000+ over daily use.
Device-agnostic (shared Moyoung code).

## Fix
`MoyoungActivitySampleProvider.java:240` — WARN -> DEBUG, and clearer wording
(old message "more than 1 ... required" contradicted its own `size() <= 1`
condition):

    - LOG.warn("Not overlaying sleep data because more than 1 sleep stage sample is required");
    + LOG.debug("Not overlaying sleep data: fewer than 2 sleep stage samples in range");

Logging-level only; no behavioural change. Compiles clean (mainlineDebug).

## Scope note
Addresses the MoyoungActivitySampleProvider warning-spam part of #5859 only. The
report's other points (duplicate SMS notifications from two apps; notification
filter "Allow All") are generic/unrelated and not covered here.
