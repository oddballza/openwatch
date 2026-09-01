# Licensing and code-origin audit

**Date:** 2026-09-01

## Summary

**No third-party code has been copied into this repository.** Consequently there is
currently no inherited license obligation. This document records the analysis that
made that the deliberate outcome.

## Gadgetbridge

* **License: GNU Affero General Public License v3.0** (`LICENSE`, verified in the
  cloned tree; per-file headers confirm, e.g. `C20Coordinator.java`:
  *"Gadgetbridge is free software: you can redistribute it and/or modify it under
  the terms of the GNU Affero General Public License … either version 3 … or (at
  your option) any later version."*)
* Upstream: `https://codeberg.org/Freeyourgadget/Gadgetbridge`
* Commit examined: `1b7ad478656fbce7ff76a330a4a0f9cf25b05eef`

### What AGPL-3.0 would have required

Had we adopted Option C (fork the protocol layer):

1. The **entire derived work** must be licensed AGPL-3.0 — this is a strong copyleft,
   not a file-level or library-level one.
2. Complete corresponding source must be offered to all users.
3. **§13 network clause:** users interacting with the work *over a network* must be
   offered the source. Not triggered by a local-only BLE app, but it would
   permanently constrain any future sync/companion service.
4. All copyright notices and license headers must be preserved verbatim.
5. Modifications must be marked with dates.

AGPL-3.0 is **incompatible** with proprietary or permissive-only relicensing. A
"lightweight fork" of Gadgetbridge's Moyoung code could not have been released under
Apache-2.0 or MIT.

### What we actually used

| Item | Use | Obligation |
|---|---|---|
| Gadgetbridge source | **Read** for analysis; quoted short excerpts in docs with attribution | None. Analysis and short attributed quotation are not derivative distribution |
| `MoyoungConstants` UUIDs (`FEEA`, `FEE1`–`FEE6`) | Cited as **facts about the hardware** | None. Protocol constants read off a device are not copyrightable expression |
| Packet framing description | Restated in prose, attributed | None |
| Gadgetbridge code | **Not copied, not adapted, not vendored** | None |

The distinction that matters: *facts about how a device behaves* (a UUID, a byte
offset, a field order) are not protected expression. *Someone's code that encodes
those facts* is. We used only the former, and cited where we learned it.

## Our own tooling

`tools/*.py` — written from scratch for this investigation against the public BlueZ
D-Bus API. No derived code. Free to license as the project chooses.

## Rules going forward

1. **Do not copy Gadgetbridge code into this repository** unless the project
   deliberately adopts AGPL-3.0 for the whole work. Publicly visible ≠ freely
   reusable.
2. Contributions flowing the *other* way — a new `MT55Coordinator` submitted
   upstream — are the clean path: authored against upstream, licensed AGPL-3.0 on
   arrival, with no obligation created here. This is a further practical argument
   for Option B.
3. Any future vendored dependency gets a row in this file: name, version, license,
   why, and what it obliges.
4. Never strip or alter a copyright header.

## Attribution

The Moyoung V2 protocol work originates with **krzys-h**
(`Gadgetbridge-MT863`, later upstreamed via PR #4070) and subsequent Gadgetbridge
contributors including Arjan Schrijver. This project's conclusions rest on their
published work, and it is cited throughout the docs.
