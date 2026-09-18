import numpy as np

# "Easy" patterns: safe vs. unsafe use visibly different, enumerable
# literal values (0777 vs 0640, http vs https, ...). Code tokens alone are
# genuinely sufficient here -- this is the class of misconfiguration a
# rule-based scanner like Checkov already catches well, comments or not.
EASY_PATTERNS = [
    {
        "resource": "deploy_directory",
        "unsafe": 'mode = "0777"',
        "safe": 'mode = "0640"',
        "comment_unsafe": "# WARNING: world-writable permissions on a deploy directory",
        "comment_safe": "# restrict directory access to the owning user and group",
    },
    {
        "resource": "api_endpoint",
        "unsafe": 'protocol = "http"',
        "safe": 'protocol = "https"',
        "comment_unsafe": "# WARNING: endpoint serves traffic over unencrypted HTTP",
        "comment_safe": "# endpoint enforces TLS for all incoming traffic",
    },
    {
        "resource": "auth_service",
        "unsafe": 'hash_algorithm = "sha1"',
        "safe": 'hash_algorithm = "sha256"',
        "comment_unsafe": "# WARNING: deprecated hash algorithm used for credential storage",
        "comment_safe": "# uses a modern, collision-resistant hash algorithm",
    },
    {
        "resource": "security_group",
        "unsafe": 'ingress_cidr = "0.0.0.0/0"',
        "safe": 'ingress_cidr = "10.0.0.0/16"',
        "comment_unsafe": "# WARNING: security group open to the entire internet",
        "comment_safe": "# restrict ingress to the internal VPC range",
    },
]

# "Hard" patterns: the code line is lexically the *same shape* for both
# labels (an opaque reference token whose numeric suffix carries no
# signal) -- only the comment says whether that reference resolves to a
# real hardcoded fallback secret or to a managed vault/KMS lookup. No
# regex or code-only classifier can tell these apart; this is what
# reproduces War et al.'s ablation finding instead of trivially avoiding
# it, and what a rule-based layer structurally cannot cover.
HARD_PATTERNS = [
    {
        "resource": "credential_store",
        "field": "password_ref",
        "comment_unsafe": "# WARNING: this ref resolves to a hardcoded fallback password used when the vault is unreachable",
        "comment_safe": "# this ref resolves via the managed secrets vault at runtime, never a literal value",
    },
    {
        "resource": "key_management",
        "field": "key_ref",
        "comment_unsafe": "# WARNING: a fallback key embedded for local testing was accidentally left enabled here",
        "comment_safe": "# key rotation and lookup is handled automatically by the KMS integration",
    },
]

FILLER_LINES = [
    'name = "{name}"',
    'region = "{region}"',
    'owner = "{owner}"',
    'tags = {{ "env": "{env}" }}',
    'instance_type = "{itype}"',
    'retention_days = {retention}',
]


def _render_filler(rng):
    return [
        line.format(
            name=f"svc-{rng.randint(1000, 9999)}",
            region=rng.choice(["us-east-1", "eu-west-1", "ap-south-1"]),
            owner=rng.choice(["platform-team", "infra-team", "app-team"]),
            env=rng.choice(["staging", "production", "dev"]),
            itype=rng.choice(["t3.medium", "m5.large", "t3.small"]),
            retention=rng.randint(7, 90),
        )
        for line in FILLER_LINES
    ]


def generate_dataset(n_samples, seed, with_comments):
    """Each sample is one synthetic IaC resource block. Half the samples
    use an "easy" pattern (safe/unsafe distinguishable from code alone);
    half use a "hard" pattern (code identical either way -- only the
    comment distinguishes them). `with_comments` controls whether that
    explanatory comment is included, mirroring War et al.'s ablation axis
    (rich text+code vs. code-only)."""
    rng = np.random.RandomState(seed)
    snippets, labels = [], []

    for _ in range(n_samples):
        is_hard = rng.randint(2)
        is_misconfigured = rng.randint(2)

        filler = _render_filler(rng)
        n_filler = rng.randint(2, 5)
        rng.shuffle(filler)
        body = filler[:n_filler]

        if is_hard:
            pattern = HARD_PATTERNS[rng.randint(len(HARD_PATTERNS))]
            ref_id = rng.randint(10000, 99999)
            config_line = f'{pattern["field"]} = "ref_{ref_id}"'
            resource = pattern["resource"]
        else:
            pattern = EASY_PATTERNS[rng.randint(len(EASY_PATTERNS))]
            config_line = pattern["unsafe"] if is_misconfigured else pattern["safe"]
            resource = pattern["resource"]

        if with_comments:
            comment = pattern["comment_unsafe"] if is_misconfigured else pattern["comment_safe"]
            config_line = f"{comment}\n{config_line}"

        lines = [f'resource "{resource}" {{'] + body + [config_line, "}"]
        snippets.append("\n".join(lines))
        labels.append(int(is_misconfigured))

    return snippets, np.array(labels)
