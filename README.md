# Google Cloud Documentation Mirror Template

This repository is a template for creating a local Markdown mirror of official Google Cloud documentation. It is designed to be automatically updated via GitHub Actions.

## Authentication Setup

This tool requires Google Cloud credentials with access to the **Developer Knowledge API**. You can authenticate using either **Workload Identity Federation** (recommended) or an **API Key**.

### Option A: Workload Identity Federation (Secure, Recommended)

Workload Identity Federation (OIDC) is the most secure way to authenticate GitHub Actions to Google Cloud, as it eliminates the need for storing long-lived secrets or keys in GitHub.

#### 1. Configure Google Cloud

Run the following commands using the `gcloud` CLI (or configure them in the Google Cloud Console):

```bash
# 1. Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --project="YOUR_PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Create an OIDC Identity Provider for GitHub
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="YOUR_PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Create a Service Account for the mirror tool
gcloud iam service-accounts create "gcp-docs-mirror-sa" \
    --project="YOUR_PROJECT_ID" \
    --display-name="GCP Docs Mirror Service Account"

# 4. Allow your GitHub repository to impersonate the Service Account
# Replace YOUR_PROJECT_NUMBER, YOUR_GITHUB_ORG, and YOUR_GITHUB_REPO with your actual values
gcloud iam service-accounts add-iam-policy-binding "gcp-docs-mirror-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --project="YOUR_PROJECT_ID" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_ORG/YOUR_GITHUB_REPO"
```

> [!NOTE]
> Ensure that the Service Account has permissions to call the Developer Knowledge API (no special IAM roles are generally required other than basic API enablement in the project, but you may grant standard viewer roles if querying other GCP resources).

#### 2. Configure GitHub Secrets

Add the following repository secrets to your GitHub repository:

*   `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full resource name of your provider:
    `projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
*   `GCP_SERVICE_ACCOUNT`: The email address of your service account:
    `gcp-docs-mirror-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`

---

### Option B: API Key (Simple Setup)

#### 1. Create the API Key

You can create a restricted API key using the `gcloud` CLI:

```bash
gcloud services api-keys create \
    --project=your-project-id \
    --display-name="Developer Knowledge API Key" \
    --api-target=service=developerknowledge.googleapis.com
```

#### 2. Configure GitHub Secrets

##### Via Web Interface
1.  Copy the generated API key.
2.  In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions**.
3.  Add a **New repository secret**:
    *   Name: `DEVELOPERKNOWLEDGE_API_KEY`
    *   Value: (Your API key)

##### Via GitHub CLI (`gh`)
If you have the `gh` CLI installed, you can set the secret directly:

```bash
gh secret set DEVELOPERKNOWLEDGE_API_KEY --body "YOUR_API_KEY"
```

---

## Setup Instructions

1.  **Create a new repository** using this template.
2.  **Modify `settings.toml`**:
    *   Replace `YOUR_PRODUCT` with the actual path component of the documentation (e.g., `spanner`, `bigquery`).
    *   Adjust `seeds` and `prefixes` as needed.
3.  **Adjust Update Schedule**:
    *   Edit `.github/workflows/update-mirror.yml`.
    *   **Crucial**: If you are maintaining multiple mirrors with the same API key, **offset the cron schedules** (e.g., `0 1 * * *`, `0 2 * * *`) to avoid simultaneous API requests that could exhaust your quota.
4.  **Configure GitHub Secrets**:
    *   Follow either **Option A (Workload Identity Federation)** or **Option B (API Key)** above to set up the necessary secrets in your GitHub repository.
5.  **Enable GitHub Actions**:
    *   Go to the `Actions` tab and enable workflows.
    *   The mirror will automatically update according to your schedule, or you can trigger it manually via `workflow_dispatch`.

## Quota Management

The `gcp-docs-mirror-tools` is configured to respect quota limits, but simultaneous runs of multiple repositories will bypass these safety mechanisms. Always ensure that only one mirror update is running at any given time if they share the same API key.

## Manual Run

If you have Go installed locally, you can run the mirror script manually:

```bash
export DEVELOPERKNOWLEDGE_API_KEY=your_api_key
./mirror.sh
```

## Credits

This mirror system is powered by [gcp-docs-mirror-tools](https://github.com/apstndb/gcp-docs-mirror-tools).

## License

The documentation content collected in this repository is mirrored from Google Cloud Documentation according to the [Google Developers Site Policies](https://developers.google.com/terms/site-policies).
- Documentation content is licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Code samples are licensed under the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0).
