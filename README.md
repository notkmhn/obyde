# obyde

A minimal tool to convert a "standardly" configured [Obsidian](https://obsidian.md/) vault to a Jekyll-based blog.

## Installation
Install obyde using `pip`:

```sh
pip install git+https://github.com/khalednassar/obyde
```

Or using `pipenv`:

```sh
pipenv install git+https://github.com/khalednassar/obyde#egg=obyde
```

## Caveat
`obyde` is mainly meant to support easy "default" Obsidian vault to Jekyll _blog_ conversions. This means that, by default, it will have to create Jekyll posts (normally under `_posts`), which require their filenames to have a "post date".
This is done by utilizing frontmatter in the Obsidian markdown notes, which means that each note must have a frontmatter section with at least a date key-value pair as such:
```md
---
date: 2021-02-13

---
```
Additionally, currently only dates of the format `YYYY-MM-DD` are supported.

## Usage
Copy the `config.yaml.sample` file and change the paths to align with your set up or copy this sample configuration:

```yaml
vault:
        path: "/path/to/vault/root/" # Path to the Obsidian vault root. Markdown file discovery will start at this directory recursively.
        asset_path: "/path/to/vault/attachments/" # Path to the Obsidian vault attachments folder
        excluded_subdirectories: # Optional: list of excluded subdirectories of the Obsidian vault root
                - .trash
output:
        post_output_path: "/path/to/jekyll/_posts/" # Path to the Jekyll posts directory
        asset_output_path: "/path/to/jekyll/assets/" # Path to the blog assets directory, copied from the Obsidian attachments folder
        relative_asset_variable: "site.blog_assets_location" # Optional: a Jekyll variable pointing to the relative URL prefix for blog assets without a trailing slash.
```

Write your posts in the Obsidian vault then simply use `obyde -c <path to config.yaml>` to move the vault to the configured Jekyll blog directory.