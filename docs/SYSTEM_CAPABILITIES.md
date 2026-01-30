# System Capabilities & Boundaries

## What the System DOES
1.  **Multi-Tenant Partitioning**: physically separates data files per `tenant_id`.
2.  **Deterministic Invariants**: Alerts are derived strictly from timestamps and state transitions (e.g., SLA breaches), never "guessed."
3.  **Idempotent ERP Sync**: Uses the `original_event_id` as a persistence marker to ensure the ERP system is notified exactly once per hire.
4.  **Restart Safety**: The state is reconstructed from the append-only JSON logs on every sync, making it resilient to server crashes.
5.  **Traceable Explainability**: Every signal can be traced back to its root HR event history.

## What the System DOES NOT Do
1.  **No AI/Heuristics**: Does not predict candidate behavior; only acts on factual data.
2.  **No Real-Time ERP Push**: Uses a "Sync Pipeline" model (triggered manually or by cron) rather than real-time webhooks, favoring stability and batch-validation over millisecond latency.
3.  **No Role-Based Authorization (PoC Boundary)**: While it demonstrates tenant isolation, it currently lacks a full JWT-based Auth system (UI role badges are visual indicators only).
4.  **No Distributed Locking**: In its current file-based form, it is designed for a single instance (Stateful Service) rather than a horizontally scaled cluster.

## Success Metric
- **Zero Duplicate ERP Signals**: Verified by Idempotency keys.
- **Zero Tenant Leaks**: Verified by strict path-based storage isolation.

## Day 1 Integration Hardening (Completed)
- **Mandatory Tenant Context**: All event contracts (SHORTLISTED, CANDIDATE_STUCK, EMPLOYEE_CREATED) now require `tenant_id`.
- **Real SLA Invariants**: Replaced placeholder alerts with real state-check logic (e.g., Shortlisted for > 3 days).
- **Restart-Safe Idempotency**: ERP signals are persisted and checked before re-emission, ensuring zero duplicates even after a full system restart.
