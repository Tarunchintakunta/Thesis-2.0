import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Comment-independent signatures for the four "easy" enumerable patterns
# in src/data/iac_dataset.py (EASY_PATTERNS). These match the literal
# misconfigured value regardless of whether an explanatory comment is
# present. They cannot, by construction, say anything about the "hard"
# patterns (HARD_PATTERNS) -- those use an opaque reference token that is
# lexically identical whether safe or misconfigured, which no fixed regex
# can distinguish. That's deliberate: it's what keeps the hybrid detector
# honest about what it can and can't fix (see README / final report).
RULE_PATTERNS = [
    re.compile(r'mode\s*=\s*"0?777"'),                        # world-writable permissions
    re.compile(r'protocol\s*=\s*"http"'),                      # unencrypted protocol
    re.compile(r'hash_algorithm\s*=\s*"(sha1|md5)"'),          # deprecated hash algorithm
    re.compile(r'ingress_cidr\s*=\s*"0\.0\.0\.0/0"'),          # world-open ingress
]


def rule_based_flag(snippet):
    return any(p.search(snippet) for p in RULE_PATTERNS)


class MLDetector:
    """Baseline reproduction: a text classifier over the IaC snippet, in
    the same TF-IDF-based family War et al. (2025) use as their prior-work
    baseline (their CodeBERT/LongFormer results are reproduced only
    qualitatively here, given no GPU/model-download budget for this
    project -- see README for that scope note). Trained separately on
    with-comments vs. code-only snippets to reproduce their ablation."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(token_pattern=r"[A-Za-z0-9_./:\-]+")
        self.model = LogisticRegression(max_iter=1000)

    def fit(self, snippets, labels):
        X = self.vectorizer.fit_transform(snippets)
        self.model.fit(X, labels)
        return self

    def predict(self, snippets):
        X = self.vectorizer.transform(snippets)
        return self.model.predict(X)

    def predict_proba(self, snippets):
        X = self.vectorizer.transform(snippets)
        return self.model.predict_proba(X)[:, 1]


class HybridDetector:
    """Improvement: addresses the paper's own ablation finding directly --
    precision collapses without natural-language context because the
    text-only model has nothing but code tokens to go on, and over-flags
    on ordinary code. A plain OR of "rule fires" with "ML predicts
    misconfigured" would only ever add false positives on top of an
    already-low-precision model, making things worse, not better. Instead:
    trust the comment-independent rule layer whenever it fires (it doesn't
    need comments to begin with), and only fall back to the ML classifier
    -- at a stricter confidence threshold than a plain 0.5 cutoff -- for
    snippets the rule layer doesn't recognise at all. This is what lets
    precision recover once comments are stripped: the unreliable low-
    confidence ML guesses that drove false positives get filtered out
    instead of being trusted outright."""

    def __init__(self, ml_detector, ml_threshold=0.8):
        self.ml_detector = ml_detector
        self.ml_threshold = ml_threshold

    def predict(self, snippets):
        probs = self.ml_detector.predict_proba(snippets)
        return [
            1 if (rule_based_flag(s) or p > self.ml_threshold) else 0
            for s, p in zip(snippets, probs)
        ]
