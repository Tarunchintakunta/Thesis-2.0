package terraform.gate

import data.terraform.encryption_at_rest as enc
import data.terraform.overpermissive_access as oa
import data.terraform.public_storage as ps
import data.terraform.weak_logging as log
import rego.v1

# CI gate: any category deny fails the module.
deny contains msg if some msg in ps.deny

deny contains msg if some msg in oa.deny

deny contains msg if some msg in enc.deny

deny contains msg if some msg in log.deny

violations := deny

blocked if count(deny) > 0
