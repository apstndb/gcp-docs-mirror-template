# Google Cloud Documentation Mirror Template

This repository is a template for creating a local Markdown mirror of official Google Cloud documentation. It is designed to be automatically updated via GitHub Actions.

## Setup Instructions

1.  **Create a new repository** using this template.
2.  **Modify `settings.toml`**:
    *   Replace `YOUR_PRODUCT` with the actual path component of the documentation (e.g., `spanner`, `bigquery`).
    *   Adjust `seeds` and `prefixes` as needed.
3.  **Adjust Update Schedule**:
    *   Edit `.github/workflows/update-mirror.yml`.
    *   **Crucial**: If you are maintaining multiple mirrors with the same API key, **offset the cron schedules** (e.g., `0 1 * * *`, `0 2 * * *`) to avoid simultaneous API requests that could exhaust your quota.
4.  **Configure GitHub Secrets**:
    *   Go to `Settings` -> `Secrets and variables` -> `Actions`.
    *   Add a **New repository secret**:
        *   Name: `DEVELOPERKNOWLEDGE_API_KEY`
        *   Value: Your Google Cloud Developer Knowledge API Key.
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
