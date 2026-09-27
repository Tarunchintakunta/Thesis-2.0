# AWS mapping stubs (not applied at floor)

| Local | AWS (CA mapping) |
|-------|------------------|
| JWT HS256 | Cognito / API Gateway JWT authorizer |
| Middleware | Lambda / ECS service |
| RLS store | RDS PostgreSQL with RLS |
| Quota engine | ElastiCache Redis |

Apply only on student account; destroy after; never commit secrets.
