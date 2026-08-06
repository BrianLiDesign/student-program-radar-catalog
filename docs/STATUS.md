# Program Status Semantics

Each record uses one of the status values defined in `data/schema.json`:

- `Accepting`: The source indicates applications are currently open.
- `Rolling`: Applications are accepted without a single fixed deadline.
- `Cohort upcoming`: A future cohort is announced, but applications are not currently open.
- `Closed`: Applications are closed and the record belongs in the archived catalog.
- `Unknown`: The available source does not establish the current application status.

Status values are snapshots. Always consult `last_verified`, `source_url`, and the official application page before relying on a listing.
