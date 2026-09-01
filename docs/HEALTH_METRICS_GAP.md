# Health metrics — Garmin-style features on MT55

Prompted by a request for Garmin Connect-style **Body Battery**, sleep score,
HRV status and similar metrics.

## The key finding: the UI already exists

Gadgetbridge already ships a complete **Body Energy** (its name for Body Battery)
data model, storage and UI, plus HRV:

```
model/BodyEnergySample.java                    entities/AbstractBodyEnergySample.java
activities/charts/BodyEnergyFragment.java      activities/charts/BodyEnergyCollectionFragment.java
activities/charts/BodyEnergyPeriodFragment.java adapter/BodyEnergyFragmentAdapter.java
entities/AbstractHrvValueSample.java           entities/AbstractHrvSummarySample.java
adapter/HrvStatusFragmentAdapter.java          export/FitExporter.java (exports body energy)
```

These are wired into `DashboardFragment` and `DefaultChartsProvider`. So **no
charting, storage or export work is needed** — Body Battery already renders for
devices that supply the data (Garmin, Huawei, Xiaomi). The gap for MT55 is purely
a **data source**.

## What MT55 can and cannot supply

| Metric | Source on MT55 | Status |
|---|---|---|
| Steps / distance / calories | `CMD_SYNC_PAST_SLEEP_AND_STEP`, `FEE1` | **Verified working** |
| Heart rate + history | Moyoung HR commands | Available (flags must be on — see below) |
| Sleep + stages (incl. REM) | `FetchDataOperation.decodeSleep()` | Available |
| Stress | Moyoung stress commands | Available |
| SpO2 / blood pressure | Manual measurement commands | Available |
| **HRV (RR intervals)** | **none** | **Not exposed.** No `CMD_*` for HRV exists |
| **Body Battery** | **none** | **Not exposed.** No such command exists |
| **Sleep score** | none from device | Derivable on-phone from sleep stages |
| Pulse Ox acclimation | none | Garmin-specific, needs altitude + continuous SpO2 |

I grepped `MoyoungConstants.java` (all 82 commands) for
`HRV|SCORE|ENERGY|FATIGUE|RECOVER|VO2|RESTING` — no matches beyond ordinary
movement/HR commands. The protocol simply does not carry these.

## Honest assessment of Body Battery

Body Battery is **Garmin's proprietary metric**, licensed from Firstbeat
Analytics. Its core input is **beat-to-beat HRV**, which MT55 does not expose —
the watch reports averaged BPM, not RR intervals. A byte-accurate reproduction is
therefore impossible on this hardware, and any claim otherwise would be false.

What *is* achievable is a **derived energy score** computed on the phone from the
inputs MT55 does provide:

```
stress history  ─┐
sleep stages    ─┼─► local model ──► BodyEnergySample rows ──► existing GB UI
HR + resting HR ─┤
activity/steps  ─┘
```

This is a genuine, useful metric, and it writes into the Body Energy tables that
already exist. It must be labelled as an OpenWatch-derived estimate, not as
Garmin Body Battery — the numbers will not match a Garmin, and pretending they
would is the one thing to avoid.

**Caveat worth stating plainly:** MT55's stress and sleep values are themselves
vendor-computed from the same optical sensor, with unknown quality. A derived
score inherits that uncertainty. Treat it as a trend indicator, not a measurement.

## Practical order of work

1. **Turn on what already exists.** `supportsHeartRateHistory()` defaults to
   `false` in `AbstractMoyoungDeviceCoordinator` and gates HR fetching entirely
   (`FetchDataOperation.java:73`). The `MT55Coordinator` in
   `patches/0001-moyoung-add-mt55-support.patch` sets it — and
   `supportsHeartRateStreaming()` — to `true`. Verify on hardware first; this
   alone may deliver most of the missing charts.
2. **Confirm stress and REM sleep** actually populate, then keep those flags.
3. **Sleep score** — derive from existing sleep-stage data. Self-contained.
4. **Derived energy score** — only after 1-3 produce trustworthy inputs.

Steps 1 and 2 are configuration, not new protocol work. Steps 3 and 4 are
app-level features and would be the strongest argument for a small Gadgetbridge
fork, since a derived-metric estimator is unlikely to be accepted upstream.
