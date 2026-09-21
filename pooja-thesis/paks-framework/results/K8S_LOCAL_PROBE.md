# Local Kubernetes probe — Pooja PAKS

**UTC:** 2026-09-21T11:49:18.433608+00:00

## Verdict

- Live kind apply possible: **False**
- Live minikube apply possible: **False**
- Live apply performed this pass: **False**
- Reason: kind/minikube missing and/or Docker daemon not running — stay on dry-run

## Binaries

- kind: `None`
- minikube: `None`
- kubectl: `/usr/local/bin/kubectl`
- docker: `/usr/local/bin/docker`

## Docker daemon

```
Cannot connect to the Docker daemon at unix:///Users/valletivarish/.docker/run/docker.sock. Is the docker daemon running?

```

## kubectl cluster-info

```
E0921 17:19:19.108846   47708 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E0921 17:19:19.109469   47708 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E0921 17:19:19.110403   47708 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"http://localhost:8080/api?timeout=32s\": dial tcp [::1]:8080: connect: connection refused"
E0921 17:19:19.110794   47708 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"http://localhost:8080/api?timeout=32s\": dial t
```

## Implication for formal CA2

Formal method still requires a Kubernetes environment (AWS EC2 + S3 + CloudWatch).
This host cannot raise dry-run → live scale patches without kind/minikube **and** a
running Docker (or another container runtime). Adaptive Scale JSON remains recorded
under `formal_k8s_dry_run.json` with `live_apply=false`.
