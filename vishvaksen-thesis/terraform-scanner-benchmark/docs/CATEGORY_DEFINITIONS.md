# Category definitions

Conditioning factor in the formal CA2 (Buhler et al. 2025; Verdet et al. 2025):
public storage, over-permissive access, encryption at rest, weak logging.

OPA policies encode **these definitions**, not module IDs.

| ID | Category | Insecure if | Secure counterpart |
|----|----------|-------------|--------------------|
| PS | public_storage | Resource is reachable from the public internet or a `Principal` of `*` | Private ACL/policy, public-access block on, `publicly_accessible=false`, no world launch permission |
| OA | overpermissive_access | Identity or network policy grants world or wildcard admin | CIDR limited to RFC1918; IAM actions/resources enumerated; no AdministratorAccess |
| ENC | encryption_at_rest | Data-at-rest encryption disabled or SSE resource absent | `encrypted=true` / SSE resource present / KMS key set |
| LOG | weak_logging | Audit/access/flow logs disabled or required logging resource absent | Trail validation on, flow logs present, access logs enabled, log exports non-empty |

Severity (provider-guidance inspired, not a CVSS score):

- HIGH: public data plane, wildcard admin, unencrypted primary datastore
- MEDIUM: missing access logs, public IP on compute, SNS/SQS SSE
- none: secure variant

OPA does **not** deny values that are clearly `var.*` references (unknown).
That is a documented false-negative class (data-flow indirection), not an
accident.
