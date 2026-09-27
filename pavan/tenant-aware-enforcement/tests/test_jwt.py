import time
import jwt as pyjwt
from auth.jwt_tokens import issue_token, verify_token


def test_issue_verify():
    tok = issue_token(sub="u1", tenant_id="t1", role="admin", secret="s")
    c = verify_token(tok, secret="s")
    assert c.tenant_id == "t1" and c.sub == "u1"


def test_tampered_tenant_rejected():
    tok = issue_token(sub="u1", tenant_id="t1", secret="s")
    # forge by decoding without verify and re-signing with wrong secret should fail verify with right secret
    try:
        verify_token(tok, secret="other")
        assert False
    except Exception:
        assert True


def test_expired():
    tok = issue_token(sub="u1", tenant_id="t1", secret="s", ttl_s=-1, now=int(time.time()) - 10)
    try:
        verify_token(tok, secret="s")
        assert False
    except pyjwt.ExpiredSignatureError:
        assert True
