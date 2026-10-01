# Academic Door Composer Public Runner Bootstrap

Status: implementation template authorized by Decision 0020.

This directory is a staging copy for the dedicated PUBLIC execution-only repository:

`academic-door/academic-door-composer-runner`

When the public repository exists, copy the contents of this directory to its repository root. The private Composer repository remains the sole canonical authority for application code, normalized private data, Worker/D1 behavior, publication state semantics, and runtime acceptance.

## Security contract

- Fixed private source: `academic-door/academic-door-composer`.
- Source credential: Composer repository only, Contents read-only.
- No arbitrary repository/ref/workflow input; dispatch payload is not consumed by the production controller.
- Production reconcile triggers: request-only `repository_dispatch` (`composer-reconcile`) + hourly offset schedule + owner `workflow_dispatch`.
- Production secrets are never available to PR/fork workflows.
- Private checkout uses `persist-credentials: false` and exists only in the ephemeral runner workspace.
- No private Composer payload is committed or uploaded as an artifact.
- Cloudflare credentials exist only in the public runner's `production` environment.
- Runtime acceptance is recorded as public-safe JSON in one bounded GitHub issue; it contains only private source SHA, accepted timestamp, workflow run URL, runtime origin, and accepted state.

## Required production environment secrets

Create environment `production` and configure:

- `COMPOSER_SOURCE_TOKEN`: fine-grained GitHub token scoped only to `academic-door/academic-door-composer`, Contents read-only.
- `CLOUDFLARE_API_TOKEN`: existing least-privilege Composer Worker + D1 deploy token.
- `CLOUDFLARE_ACCOUNT_ID`: existing Composer Cloudflare account id.

Do not copy or expose secret values in issues, logs, artifacts, repository files, or chat.

## Initial acceptance

The first successful reconcile must resolve current private Composer `main` itself, deploy that exact SHA, run the full Composer validation/regression suite, apply D1 migrations, and verify unauthenticated requests to UI/data/API are challenged by Cloudflare Access.

Composer incident #30 additionally requires an authenticated product readback showing NBER 2026-09-28 with 43 papers before closure.

## Branch/rules safety

The public runner default branch is a security-sensitive deployment controller. Configure a ruleset that blocks force-push/deletion and requires pull-request review for workflow/controller changes. The production workflow itself does not write repository contents; its public-safe acceptance marker is maintained in one GitHub issue.

## Obsolete private lane

Do not disable the private Composer deploy workflow until the public runner has production-accepted current private main. After acceptance, ⑥ should fence/retire private automatic deploy triggers while preserving a safe rollback/manual path as decided by owner evidence.
