# Changelog

All notable changes to **kedrogen** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Support for remote Git template repositories.
- Support for `--checkout`, `--directory`, `--telemetry` flags, similar to `kedro new`

---

## [0.2.0] 2025-07-12

### Added
- **Remote template support**  
  You can now use:
  - Remote git repository (gitlab, github, bitbucket etc) URLs (e.g. `https://github.com/user/repo`, `gh:user/repo`)
  - `.zip` archives (local or remote)
  - `file://` URLs
  - or, any type of URLs that [cookiecutter supports](https://cookiecutter.readthedocs.io/en/stable/usage.html#works-directly-with-git-and-hg-mercurial-repos-too)

  as valid inputs to the `template_path` argument. `kedrogen` will automatically detect, fetch, and use them.

- **Version flag**  
  Added a `--version` (or `-v`) option to display the installed version of `kedrogen` directly from the command line.

---

## [0.1.0] 2025-07-07

### Added

- Added flags:
  - `--verbose` / `-v`: show detailed steps of the generation process.
  - `--quiet` / `-q`: suppress all output except warnings and errors.

---

## [0.0.9] - 2025-07-05

### Added
- First public release of `kedrogen` 🎉
- CLI to generate a Kedro project from a Cookiecutter template into the current directory.
- Auto-detects and validates current directory name to be used as `project_name`.
- Extracts and sets essential fields: `project_name`, `repo_name`, `python_package`, and `kedro_version` for cookiecutter context.
- Dynamically detects optional template fields (e.g., `tools`, `example_pipeline`) and sets them to `None` for prompting.
- Supports rich CLI feedback using `rich.print`.
- Automatically handles moving generated project files into current directory if template creates a subfolder.
- Prompts user before overwriting existing files.


