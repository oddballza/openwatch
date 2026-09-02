# Investigation: body-composition support in Gadgetbridge

## Problem
GB stores WEIGHT ONLY. `WeightSample` = `weightKg`; even `MiCompositionScaleDeviceSupport`
reads the standard Body Composition Measurement (0x2A9C) but parses only the weight
field (offset 11) and discards impedance/fat/etc. No body-composition model exists.
So a BIA scale (e.g. the "Health Scale" / 1byone on 0xFFF0, or Mi Composition Scale)
can contribute weight only.

## Feasibility: YES - building blocks present
- Schema: greenDAO generator (GBDaoGenerator, Schema v138). Weight entities add float
  properties; extend AbstractWeightSample + bump v138->v139 + migration.
- Profile for BIA math: ActivityUser has getHeightCm/getAge/getGender/getWeightKg.
- Algorithms: openScale (GPLv3, compatible with GB AGPLv3) has impedance->fat/muscle/water.
- Health Connect: has BodyFatRecord, LeanBodyMassRecord, BoneMassRecord,
  BodyWaterMassRecord, BasalMetabolicRateRecord.

## Scope (multi-part feature, staged)
1. Schema/DB: nullable impedance, bodyFatPercent, muscleMass, bodyWaterPercent,
   boneMass, bmr, visceralFat on AbstractWeightSample + entities; v139 + migration.
2. Model: extend WeightSample interface (default getters).
3. Computation: impedance + profile -> derived metrics (port openScale formulas, attributed).
4. Device support: MiComposition keep impedance (currently dropped); new 0xFFF0 Health
   Scale coordinator populates fields.
5. UI: body-composition chart/view.
6. Health Connect: new syncers alongside WeightSyncer.

## Upstream context
- #6393 "Parse and store impedance from Mi Body Composition Scale 2 (and other BIA
  scales)" - OPEN, no comments, unclaimed. Exactly this feature.
- #6349 - joserebelo (maintainer) engaged; said the deeper change is "a larger change
  than I can do right now". Acknowledged gap, not rejected.

## Recommendation
Worth doing (benefits all BIA scales). Core-schema + new metric family => propose the
DATA MODEL DESIGN on #6393 and get maintainer (joserebelo) buy-in BEFORE implementing.
Then stage: schema+migration -> computation -> one scale populating -> UI -> HC sync.
The "Health Scale" (1byone, 0xFFF0) coordinator rides on top once the model exists.

Reference (protocol, legitimate - openScale GPLv3):
1byone/"Health Scale": service 0xFFF0, notify 0xFFF4 (CF frames: weight=(b3|b4<<8)/100,
impedance=(b2<<8|b1)*0.1), write 0xFFF1 (init/clock, F2 00 history, F2 01 clear).
