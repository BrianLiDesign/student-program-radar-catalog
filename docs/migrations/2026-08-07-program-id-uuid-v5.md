# Program ID migration — UUID v5 (2026-08-07)

One-time migration from legacy placeholder UUIDs to canonical UUID v5 IDs
derived from `company|name` via `scripts/program_ids.py`.

**Migrated on:** 2026-08-07

## Downstream consumers

- Merge/update key is now the canonical UUID v5 for `company|name`.
- No further ID changes are planned without a new migration.

## Mapping

| Old ID | New ID (UUID v5) | Company | Name | Key |
| --- | --- | --- | --- | --- |
| `d290f1ee-6c54-4b01-90e6-d701748f0851` | `b354e3ff-6134-5f1f-8e81-8a72f912bffb` | Microsoft | Microsoft Learn Student Ambassador | `microsoft|microsoft learn student ambassador` |
| `d290f1ee-6c54-4b01-90e6-d701748f0852` | `5eef1a7f-e69f-5d32-a81f-fe44c6a228e0` | Microsoft | Microsoft Imagine Cup | `microsoft|microsoft imagine cup` |
| `d290f1ee-6c54-4b01-90e6-d701748f0854` | `4d972b1c-cac2-5e37-badb-b908611a5168` | Microsoft | Microsoft LEAP Apprenticeship Program | `microsoft|microsoft leap apprenticeship program` |
| `550e8400-e29b-41d4-a716-446655440000` | `19a10f31-b04b-5135-b79f-555cff1c3bad` | Adobe | Adobe Student Ambassador | `adobe|adobe student ambassador` |
| `550e8400-e29b-41d4-a716-446655440001` | `84850930-40ad-5591-a1b3-e1f83fe611b5` | Adobe | Adobe Creative Cloud Fellowship | `adobe|adobe creative cloud fellowship` |
| `550e8400-e29b-41d4-a716-446655440002` | `7e072019-78ee-554a-a74b-496aaa552e4f` | Adobe | Adobe Design Circle | `adobe|adobe design circle` |
| `550e8400-e29b-41d4-a716-446655440003` | `1c72a7c6-5575-57fb-8c69-a367f4f21d07` | Adobe | Adobe University Outreach | `adobe|adobe university outreach` |
| `550e8400-e29b-41d4-a716-446655440004` | `07251db3-853b-52b6-864a-192923196f56` | Adobe | Adobe Ideapalooza | `adobe|adobe ideapalooza` |
| `3ba33b4a-3c1a-5555-8e1b-6b2a81b144c3` | `b2c10956-f96b-5c5a-96ef-2db2843c0620` | Apple | Apple Education | `apple|apple education` |
| `3ba33b4a-3c1a-5555-8e1e-6c0082cea8c9` | `c57f4602-90fc-5f7b-8c70-2f3b0351f6e2` | Netflix | Netflix Campus Ambassador | `netflix|netflix campus ambassador` |
| `d290f1ee-6c54-4b01-90e6-d701748f0855` | `338e6816-b56f-5dc5-97b2-a724e667bbfa` | Microsoft | Microsoft University Recruiting Programs | `microsoft|microsoft university recruiting programs` |
| `d290f1ee-6c54-4b01-90e6-d701748f0853` | `7fc94ab4-51a7-5733-bd1b-69821cfb5c12` | Microsoft | Microsoft Garage Internship | `microsoft|microsoft garage internship` |
