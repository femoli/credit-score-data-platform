# Contributing Guidelines

## Branch Strategy

This project follows a simplified Git workflow:

- `main`: stable production-ready branch.
- `develop`: integration branch.
- `feature/*`: feature development branches.

Development must happen in feature branches created from `develop`.

## Branch Naming

Examples:

- `feature/project-bootstrap`
- `feature/data-ingestion`
- `feature/bronze-layer`
- `feature/silver-processing`
- `feature/gold-modeling`
- `feature/airflow-orchestration`
- `feature/docker-environment`

## Commit Convention

This project uses Conventional Commits.

Examples:

```text
chore: initialize project structure
feat: implement kaggle ingestion
fix: handle missing customer identifiers
docs: update medallion architecture documentation
test: add validation unit tests
refactor: improve transformation logic
```

## Pull Request Flow
1. Create a feature branch from develop.
2. Implement the changes.
3. Update documentation when needed.
4. Run tests and checks.
5. Open a Pull Request into develop.
6. Merge into main only after the feature is stable.