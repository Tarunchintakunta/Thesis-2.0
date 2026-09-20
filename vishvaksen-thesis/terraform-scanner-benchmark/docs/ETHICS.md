# Ethics

- No participants, no personal data, no production configs, no third-party
  repository copies. Corpus is purpose-built synthetic HCL.
- Dual-use: insecure cloud examples. Categories are already in AWS/CIS
  documentation. Modules are **evaluation of detectors only**.
- **No live infrastructure is applied.** Do not `terraform apply`.
- `terraform plan` against a live account is also out of scope here.
- Parser/HCL load is local. Optional `terraform validate` would download
  providers only; this pass does not require it.
- Named tools (Checkov, tfsec, OPA) are used at shipped defaults; versions
  are pinned; results are per category, not a single vendor ranking.
