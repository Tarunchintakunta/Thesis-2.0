# Checklist scoring sheet (blank template)

Copy one sheet per module. Fill by hand or paste into a CSV with the same
column names. Follow `docs/MANUAL_CHECKLIST.md`.

---

**Rater ID:** _______________  
**Date:** _______________  
**Pass type:** [ ] Independent human   [ ] Training only

**module_id:** _______________  
**category:** [ ] public_storage  [ ] overpermissive_access  
              [ ] encryption_at_rest  [ ] weak_logging  
**rel_path:** `corpus/________________/main.tf`  
**Start time:** _______ **End time:** _______

### Item ticks (category items only — mark N/A for other categories)

| # | Item (short) | Pass | Fail | N/A | Evidence line / note |
|--:|--------------|:----:|:----:|:---:|----------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |
| 9 | | | | | |

### Module verdict

- [ ] **Pass (secure)** — no Fail ticks  
- [ ] **Fail (insecure)** — ≥1 Fail tick  

**Predicted label for κ / metrics:** [ ] secure  [ ] insecure  

**Notes (var.* indirection, ambiguity):**  
_______________________________________________

**Rater signature / initials:** _______________

---

## CSV column schema (batch export)

```text
rater_id,date,pass_type,module_id,category,rel_path,item_fails,verdict,predicted_label,notes,seconds
```

`pass_type` must be `independent_human` or `nonindependent_scripted` /
`nonindependent_same_author`. Never leave blank.
