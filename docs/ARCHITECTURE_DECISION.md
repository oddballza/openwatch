# ADR-001 — Do not build OpenWatch; use and extend Gadgetbridge

**Date:** 2026-09-01
**Status:** Accepted (pending owner sign-off)
**Decision:** **Option B** — Gadgetbridge supports the watch's protocol in full but
does not register its model name. Use Gadgetbridge; contribute the missing
coordinator upstream.

## Context

The brief asked for a privacy-first, ad-free Android companion app for a Da Fit
watch, but required this decision *before* implementation, and set the principle:
prefer extending an existing open-source implementation that solves 80–95% of the
problem.

Phase 1 reconnaissance ([`RESEARCH.md`](RESEARCH.md),
[`evidence/mt55-recon.md`](evidence/mt55-recon.md)) established:

* The watch reports DIS manufacturer **`MOYOUNG-V2`** — the exact literal upstream
  uses to select the V2 packet framing. Protocol identity is confirmed, not inferred.
* It exposes `0xFEEA` with `FEE1/FEE2/FEE3/FEE5/FEE6` matching `MoyoungConstants`.
* A live `FEE1` read returned 9 bytes decoding correctly under upstream's parser
  (790 steps / 655 m / 42 kcal); battery read 48 %.
* `MT55` matches **0 of 412** device-name regexes in Gadgetbridge.
* Upstream device matching is name-regex-only (`AbstractDeviceCoordinator:140-151`).

## Options considered

**Option A — Gadgetbridge already does everything.** Rejected *as literally stated*:
it cannot pair with `MT55` out of the box. Correct once the name is registered.

**Option B — Supported protocol, missing model registration. → CHOSEN.**
The gap is one regex. There is a same-day no-code workaround (bind the MAC to an
existing MTU-508 Moyoung type via `DeviceTypeDialog`), and a ~40-line upstream patch
for the durable fix.

**Option C — Fork the protocol layer into a lightweight app.** Rejected. The premise
is that upstream's architecture is oversized for the need, but the cost is inverted:
we would re-derive 82 opcodes, historical sync, workout parsing, notification
routing and settings — all already tested upstream — to gain nothing on the gap
analysis, where the "OpenWatch would add" column is empty on every row. AGPL-3.0
also means a fork cannot be quietly slimmed and relicensed
(see [`LICENSING.md`](LICENSING.md)).

**Option D — Not properly supported; reverse-engineer.** Rejected: the protocol is
already implemented and empirically validated against this watch.

## Consequences

**Positive**

* Full desired feature set immediately, from maintained and tested code.
* Every philosophy requirement in the brief — open source, no ads, no account, no
  cloud, no telemetry, local-first, data export, minimal permissions — is already
  Gadgetbridge policy. Nothing to rebuild.
* A contributed coordinator benefits every other MT55 owner.
* Near-zero maintenance burden versus owning a BLE stack.

**Negative / accepted**

* We do not control the UI. Accepted: the brief's UI goals were a means to
  ad-free local-first data, which Gadgetbridge already provides.
* ECG is unavailable — but that is a **hardware** limit (`FEE7`/`FEE8` absent), not
  fixable in any app.
* Firmware updates remain vendor-only (see `RESEARCH.md` §7).

## Next actions

1. Install Gadgetbridge; enable *Discover unsupported devices*; long-press `MT55`;
   bind its MAC to an MTU-508 Moyoung device type. Confirm connect + sync.
2. Record which capabilities actually work — this converts the *(unverified)* rows
   in [`GADGETBRIDGE_ANALYSIS.md`](GADGETBRIDGE_ANALYSIS.md) into evidence, and it is
   exactly the evidence an upstream PR needs.
3. Submit `MT55Coordinator` upstream (pattern `^MT55$`, `getMtu() = 508`, modelled on
   `C20Coordinator.java`) plus `DeviceType` entry and string resource.
4. Revisit this ADR **only** if step 1 exposes real protocol divergence.

## What is explicitly NOT being built

Phases 4–8 of the brief — the Kotlin/Compose app, Room schema, sync engine,
dashboard, notification filtering — are **not** being implemented. That is the
point of this decision. `docs/PROTOCOL_RESEARCH.md` is likewise deferred: it was
conditional on the protocol being unsupported, and it is not. The reusable output
of Phase 1 is the diagnostic tooling in `tools/`, retained for onboarding the
*next* unlisted watch.
