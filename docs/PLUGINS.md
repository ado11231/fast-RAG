# Community Plugins — fastrag

This is the official list of community-built plugins for fastrag.
To add yours, open a PR and add a row to the relevant table.

---

## Loaders

Loaders add support for new data sources beyond the built-in PDF, DOCX, TXT, and MD.

| Plugin | Source | Install | Maintainer |
|---|---|---|---|
| *be the first* | — | — | — |

---

## Embedders

Embedders add support for new embedding models and providers.

| Plugin | Provider | Install | Maintainer |
|---|---|---|---|
| *be the first* | — | — | — |

---

## Stores

Stores add support for new vector databases.

| Plugin | Database | Install | Maintainer |
|---|---|---|---|
| *be the first* | — | — | — |

---

## Chunkers

Chunkers add new text splitting strategies.

| Plugin | Strategy | Install | Maintainer |
|---|---|---|---|
| *be the first* | — | — | — |

---

## Adding Your Plugin

1. Build your plugin following the [Plugin Guide](docs/PLUGIN_GUIDE.md)
2. Publish to PyPI as `fastrag-{name}` (e.g. `fastrag-notion`)
3. Open a PR to this file with your row added to the right table
4. Include: plugin name, what source/provider/strategy it supports, PyPI install command, your GitHub handle

There is no approval process beyond the PR. If it implements the base class contract
and passes basic testing, it gets listed.
