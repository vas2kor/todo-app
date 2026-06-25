# AWS Deployment Outline

## Suggested Services

- ECS Fargate for `frontend` and `backend`
- ECR for container images
- RDS PostgreSQL for production database
- ElastiCache Redis for Socket.IO pub/sub adapter
- Application Load Balancer for routing
- Secrets Manager for OAuth and session secrets

## Production Environment Variables

- `DATABASE_URL` -> PostgreSQL DSN
- `SESSION_SECRET`
- `OAUTH_GOOGLE_CLIENT_ID`
- `OAUTH_GOOGLE_CLIENT_SECRET`
- `OAUTH_GOOGLE_REDIRECT_URI`
