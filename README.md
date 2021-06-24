# obyde

A minimal tool to convert a "standardly" configured [Obsidian](https://obsidian.md/) vault to a Jekyll or Hugo blog.

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
`obyde` is mainly meant to support easy "default" Obsidian vault to Jekyll or Hugo _blog_ conversions and it does so in an opinionated way. In order to create posts in an easy fashion, it requires that post filenames have a "post date", this is mainly to align with Jekyll, but it is also nice to use for Hugo.
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
        post_output_path: "/path/to/jekyll/_posts/" # Path to the Jekyll or Hugo posts directory
        asset_output_path: "/path/to/jekyll/assets/" # Path to the blog assets directory, copied from the Obsidian attachments folder
        relative_asset_path_prefix: "{{ site.blog_assets_location }}" # Optional: a relative URL prefix for blog assets without a trailing slash. Can also be a liquid template substitution for Jekyll.
        post_link_mode: "jekyll" # Optional, values can be either "jekyll" or "hugo" and the default is "jekyll". Sets the way post references are output.
```

Write your posts in the Obsidian vault then move the vault to the configured Jekyll or Hugo blog directory using
```sh
obyde -c <path to config.yaml>
``` 

### Options
**Regex-based find and replace transformations**: (see PR [#1](https://github.com/khalednassar/obyde/pull/1)) can be done through the frontmatter by specifying a `find` regex list and a corresponding `replace` string list of the same length. Each `find` regex will be compiled to search and replace matching instances with the string that is at the same index in the `replace` list.

For example, the following frontmatter configuraiton will replace every instance of `foo` with `baz` and every instance of `bar` and `bak` with `qux`:
```yaml
---
find:
  - foo
  - ba(r|k)
replace:
  - baz
  - qux
```
