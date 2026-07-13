# Contributing Guidelines

## 🌿 Branching Strategy

This project follows a Git Flow–inspired workflow.

```text
main
  ▲
  │
release/*
  ▲
  │
develop
  ▲
  │
feature/*
```

### Branch Types

| Branch | Purpose |
|--------|---------|
| `main` | Stable production-ready branch containing official releases. |
| `release/*` | Release stabilization, documentation updates, and final validation before merging into `main`. |
| `develop` | Integration branch for completed features. |
| `feature/*` | Development of a single feature or improvement. |

Development must always start from the `develop` branch.

---

## 🌱 Branch Naming

Examples:

```text
feature/project-bootstrap
feature/data-ingestion
feature/bronze-layer
feature/silver-processing
feature/gold-modeling
feature/gcs-integration
feature/airflow-orchestration

release/v1.0.0
release/v1.1.0
```

---

## 📝 Commit Convention

This project follows the Conventional Commits specification.

Examples:

```text
feat: implement Apache Airflow orchestration
feat: add Google Cloud Storage integration
fix: handle missing customer identifiers
docs: update project documentation
test: add Airflow task unit tests
refactor: simplify pipeline facade
chore: update project dependencies
```

---

## 🔀 Development Workflow

1. Create a feature branch from `develop`.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
```

2. Implement the feature.

3. Update the documentation when required.

4. Run all tests.

```bash
pytest
```

5. Open a Pull Request targeting `develop`.

6. Merge using **Squash and Merge**.

---

## 🚀 Release Workflow

When all planned features for a release are complete:

1. Create a release branch from `develop`.

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0
```

2. Perform the final validation:

- Documentation review
- Pipeline execution
- Airflow orchestration
- Google Cloud Storage upload
- GitHub Actions
- Unit tests
- Integration tests

3. Merge the release into `main`.

4. Create the GitHub Release.

5. Synchronize `main` back into `develop`.

```bash
git checkout develop
git merge main
git push origin develop
```

---

## ✅ Pull Request Checklist

Before opening a Pull Request, ensure that:

- All tests are passing.
- Documentation has been updated when necessary.
- New functionality includes appropriate tests.
- The branch is up to date with `develop`.
- The project executes successfully.