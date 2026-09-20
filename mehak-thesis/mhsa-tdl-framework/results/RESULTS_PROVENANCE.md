# Results provenance

- Dataset flag used for this CSV: **synthetic**
- Formal CA2 requires **Google Cluster Trace** (`--dataset gct`).
- If dataset is `synthetic`, these numbers are **artefact-as-built only** and do **not** close the GCT residual (see `../../DATA_GAPS.md`).
- Formal metric suite columns present: Accuracy, Precision, Recall, Macro-F1, ROC-AUC, Latency (ms).
- Classical RF/KNN/SVM rows are scaffold monitors on the same feature matrix; Aldomi hybrid reproduction still needs GCT feature schemas.
