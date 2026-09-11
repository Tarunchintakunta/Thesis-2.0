# Viva pack - checklist

Kondragunta Lakshmi Chaitanya - 25171216

The presentation script, demo narration and Q&A answers are the student's own
work. This is only a checklist of what to prepare and the commands that are
handy for a live demo.

## To prepare

- [ ] 10-minute presentation script
- [ ] 5-10 minute demo script
- [ ] answers for likely examiner questions: validity of forcing cold starts with a configuration update, why not provisioned concurrency, cost model and INIT billing, generalisability (one region, one provider), why the proxy benchmark is not Lambda data

## Demo commands

Show a cold and a warm REPORT line from the real stack:

```bash
aws lambda update-function-configuration --function-name coldstart-study-python-default \
  --environment "Variables={COLD_TOKEN=$(date +%s)}" >/dev/null
aws lambda wait function-updated-v2 --function-name coldstart-study-python-default
aws lambda invoke --function-name coldstart-study-python-default --cli-binary-format raw-in-base64-out \
  --payload file://payloads/fixed_payload.json --log-type Tail out.json \
  --query LogResult --output text | base64 --decode | grep REPORT     # has Init Duration
aws lambda invoke --function-name coldstart-study-python-default --cli-binary-format raw-in-base64-out \
  --payload file://payloads/fixed_payload.json --log-type Tail out.json \
  --query LogResult --output text | base64 --decode | grep REPORT     # no Init Duration
```

Without AWS (clearly synthetic):

```bash
DATA_MODE=mock python scripts/mock_cloudwatch.py --function java-default --n 6 --cold-every 3
```

Runtime gate and tests:

```bash
python scripts/check_digests.py
make test
```
