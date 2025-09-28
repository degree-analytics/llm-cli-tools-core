---
purpose:
  "Enable repositories to authenticate via GitHub App for read-only access to
  llm-cli-tools-core."
audience: "DevOps engineers, maintainers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# GitHub App Integration Guide

This guide covers how to provide read-only access to `llm-cli-tools-core` from
other repositories using a GitHub App. The initial consumers are the `mimir` and
`spacewalker` repositories, but the same setup applies to future repos.

## When to Use This

- Onboard a new repository that needs read access to llm-cli-tools-core or other
  shared libraries.
- Rotate credentials or audit GitHub App configuration for compliance.

## Prerequisites

- Organization owner rights (or delegated permission) to manage GitHub Apps.
- Access to configure organization-level secrets and variables.

## 1. Register the GitHub App

1. Go to **Organization Settings → Developer settings → GitHub Apps**.
2. Click **New GitHub App** and configure:
   - **Owner**: the same organization that owns `llm-cli-tools-core`.
   - **Repository access**: `Only on selected repositories`.
   - **Permissions**: `Metadata: Read` (implicit) and `Contents: Read`. Avoid
     granting write scopes unless a consumer requires writes later.
   - Skip webhooks unless we add event-driven behavior later.
3. Save the app registration.

## 2. Generate Credentials Once

1. From the app settings page, generate a private key
   (`Generate a private key`).
2. Store the downloaded PEM file securely; we will copy its full contents
   (including the `BEGIN/END` lines) into an organization secret.
3. Note the **App ID** and **Slug** shown on the same settings page. We use the
   App ID in workflows; the slug becomes the bot account name.

## 3. Store Shared Secrets at the Org Level

Create org-wide values so every consumer repo can reuse the same credentials:

- **Organization secret** `APP_PRIVATE_KEY`: the full PEM contents from step 2.
- **Organization variable** `APP_ID`: the numeric App ID.

Restrict access to the repositories that should be able to read
`llm-cli-tools-core` (currently `llm-cli-tools-core`, `mimir`, and
`spacewalker`). Future repos can be opted in without changing existing secrets.

## 4. Install the App Where Needed

For each repo that must read this codebase:

1. From the GitHub App settings, choose **Install App**.
2. Select the organization installation, then choose the repositories:
   - `llm-cli-tools-core`
   - `mimir`
   - `spacewalker`
   - add more repos as they are created.

The installation scopes the read token to the selected repositories only.

## 5. Use the App Token in GitHub Actions

In each consumer repo (`mimir`, `spacewalker`, etc.), update workflows that need
to clone or query this repo.

```yaml
jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ vars.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
      - name: Check out llm-cli-tools-core
        uses: actions/checkout@v4
        with:
          repository: org-name/llm-cli-tools-core
          token: ${{ steps.app-token.outputs.token }}
          path: llm-cli-tools-core
```

Replace `org-name` with the actual organization handle. The generated
installation token expires after one hour, so create it inside each job that
needs access.

### Tips

- The same token can authenticate `gh` CLI, REST API, or GraphQL calls by
  setting `GH_TOKEN` or the `Authorization: Bearer` header.
- If a workflow already has a job-wide `defaults.run.working-directory`, ensure
  the checkout path does not collide with existing directories.

## Verification

- Run the provided workflow snippet in a dry-run branch and confirm checkout
  succeeds using the GitHub App token.
- Validate that organization secrets (`APP_ID`, `APP_PRIVATE_KEY`) are scoped to
  the appropriate repositories.

## 6. Onboarding Future Repos

When a new repo needs read access:

1. Add the repo to the GitHub App installation.
2. Allow the repo to use the org secret and variable.
3. Update its workflows with the snippet above.

No new credentials are required.

## 7. Rotating Credentials

1. Generate a second private key for the app.
2. Update the `APP_PRIVATE_KEY` secret with the new PEM contents.
3. Once workflows confirm success, delete the old key from the app settings.

Keep the App ID unchanged; only the private key rotates.

## 8. Troubleshooting

- **403 Forbidden**: the app is not installed on the target repo or lacks
  `Contents: Read` permission.
- **404 Not Found**: the token is valid but the repository is not in the
  installation scope.
- **Expired token**: re-run the step; tokens last 60 minutes and cannot be
  refreshed.

Ask an org admin to review audit logs if unexpected behavior persists.
