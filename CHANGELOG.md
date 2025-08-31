## [0.4.3](https://github.com/genix-x/git-auto-flow/compare/v0.4.2...v0.4.3) (2025-08-31)


### Bug Fixes

* **commit:** correct newline characters in commit messages ([102fab5](https://github.com/genix-x/git-auto-flow/commit/102fab5fde0eb85f3d87476a74f5fa1afa834105))
* **git-utils:** add debug mode to git utils\n\nadd debug logging to git commands in git_utils.py ([f82e142](https://github.com/genix-x/git-auto-flow/commit/f82e142fe5523ac0df3ba3511091f1011cd7bbaa))
* **gitleaks:** improve gitleaks scan accuracy and reporting ([88a856b](https://github.com/genix-x/git-auto-flow/commit/88a856bf8dda76fcf189d8e4f498ee5bea7203d3))

## [0.4.2](https://github.com/genix-x/git-auto-flow/compare/v0.4.1...v0.4.2) (2025-08-24)


### Bug Fixes

* replace --staged with --log-opts for gitleaks to avoid scanning full history ([2321de1](https://github.com/genix-x/git-auto-flow/commit/2321de1cbac4bb7457b971c1a1bee675e9277030))

## [0.4.1](https://github.com/genix-x/git-auto-flow/compare/v0.4.0...v0.4.1) (2025-08-23)


### Bug Fixes

* **gitleaks:** improve gitleaks integration\n\nonly scan staged files with gitleaks ([7a73469](https://github.com/genix-x/git-auto-flow/commit/7a7346939ac6361dde8d4e5a805f9057d778facf))

# [0.4.0](https://github.com/genix-x/git-auto-flow/compare/v0.3.1...v0.4.0) (2025-08-23)


### Bug Fixes

* **git-commit-auto:** handle cases where gemini uses a field other than 'description'\n\nImproved commit message generation to handle various field names used by Gemini. ([836d728](https://github.com/genix-x/git-auto-flow/commit/836d728997257a14e2170476963cfbeb2176837e))
* **install:** remove gitleaks from package.json and add branch cleanup to feature-start ([3d72189](https://github.com/genix-x/git-auto-flow/commit/3d721899ea9902d07eed943c29408d616cd3c67d))
* **security:** improve gitleaks integration\n\nimprove gitleaks scan accuracy and output ([27f7d48](https://github.com/genix-x/git-auto-flow/commit/27f7d489458b8dd87cd6d9e536d378dd041da8ae))


### Features

* **security:** add gitleaks integration for secret scanning\n\nIntegrate Gitleaks to scan commits for secrets before pushing ([5dc6bd6](https://github.com/genix-x/git-auto-flow/commit/5dc6bd60ad213869df231b95ec9bdd2fa5b1a13c))
* **security:** add gitleaks secret scanning to prevent credential commits ([b78816d](https://github.com/genix-x/git-auto-flow/commit/b78816d399eec82886373a6d7b285ebf8faee040))

## [0.3.1](https://github.com/genix-x/git-auto-flow/compare/v0.3.0...v0.3.1) (2025-08-23)

# [0.3.0](https://github.com/genix-x/git-auto-flow/compare/v0.2.0...v0.3.0) (2025-08-22)


### Features

* **git:** add auto-delete branch feature after merge\n\nAdd functionality to automatically delete merged branches. ([b8ff6cd](https://github.com/genix-x/git-auto-flow/commit/b8ff6cd497e9e8e0b84b184874400af85501cbf6))
* **git:** add automatic cleanup after merging features\n\nImproved git workflow automation with automatic cleanup: ([5311b08](https://github.com/genix-x/git-auto-flow/commit/5311b08a060d943810b0c2edb92ef8d19418f7f9))
* **release-automation:** add automatic release PR creation with immediate merge\n\nAutomates the creation of release PRs from develop to main branch. ([8221639](https://github.com/genix-x/git-auto-flow/commit/8221639aff49cb49d0f3034fb4c0f8bbe378c5ab))
* **release:** add automated release process\n\nAutomate the release process from develop to main branch using GitHub CLI and AI. ([3c84137](https://github.com/genix-x/git-auto-flow/commit/3c8413720c803699fdcfb184aa6aa597e1624d26))

# [0.3.0](https://github.com/genix-x/git-auto-flow/compare/v0.2.0...v0.3.0) (2025-08-22)


### Features

* **git:** add auto-delete branch feature after merge\n\nAdd functionality to automatically delete merged branches. ([b8ff6cd](https://github.com/genix-x/git-auto-flow/commit/b8ff6cd497e9e8e0b84b184874400af85501cbf6))
* **git:** add automatic cleanup after merging features\n\nImproved git workflow automation with automatic cleanup: ([5311b08](https://github.com/genix-x/git-auto-flow/commit/5311b08a060d943810b0c2edb92ef8d19418f7f9))

# [0.3.0](https://github.com/genix-x/git-auto-flow/compare/v0.2.0...v0.3.0) (2025-08-22)


### Features

* **git:** add auto-delete branch feature after merge\n\nAdd functionality to automatically delete merged branches. ([b8ff6cd](https://github.com/genix-x/git-auto-flow/commit/b8ff6cd497e9e8e0b84b184874400af85501cbf6))
* **git:** add automatic cleanup after merging features\n\nImproved git workflow automation with automatic cleanup: ([5311b08](https://github.com/genix-x/git-auto-flow/commit/5311b08a060d943810b0c2edb92ef8d19418f7f9))

# [0.3.0](https://github.com/genix-x/git-auto-flow/compare/v0.2.0...v0.3.0) (2025-08-22)


### Features

* **git:** add auto-delete branch feature after merge\n\nAdd functionality to automatically delete merged branches. ([b8ff6cd](https://github.com/genix-x/git-auto-flow/commit/b8ff6cd497e9e8e0b84b184874400af85501cbf6))
* **git:** add automatic cleanup after merging features\n\nImproved git workflow automation with automatic cleanup: ([5311b08](https://github.com/genix-x/git-auto-flow/commit/5311b08a060d943810b0c2edb92ef8d19418f7f9))

# [0.2.0](https://github.com/genix-x/git-auto-flow/compare/v0.1.0...v0.2.0) (2025-08-22)


### Features

* **git:** add automated git workflow with improved installation\n\nImproved installation process: ([60279e5](https://github.com/genix-x/git-auto-flow/commit/60279e5cb40d5ef286d416e3aac177c7f9dc7b4e))
* **git:** add git alias for pr creation\n\nadd a new git alias 'pr' which is shorthand for 'pr-create-auto' ([666828c](https://github.com/genix-x/git-auto-flow/commit/666828c5ae2bc9cb81deaffb83fc0fbbac79ec8d))

# 1.0.0 (2025-08-22)


### Bug Fixes

* add package-lock.json for GitHub Actions ([c0a2a2d](https://github.com/genix-x/git-auto-flow/commit/c0a2a2dd937c828b369020ff75739d59210774f4))
* detect main branch if develop doesn't exist ([f0644a4](https://github.com/genix-x/git-auto-flow/commit/f0644a4a279a9bdb3d3ce264e07da92a77668114))
* remove invalid --delete-branch flag from gh pr create ([87accdb](https://github.com/genix-x/git-auto-flow/commit/87accdb9581d9e1ac479edff1431e89cb65a6717))
* switch to pnpm for semantic-release workflow ([78d3ebd](https://github.com/genix-x/git-auto-flow/commit/78d3ebd9b2aaea1791bc229c34cb0aee9b56b999))


### Features

* add semantic-release and interactive API key setup ([dd90291](https://github.com/genix-x/git-auto-flow/commit/dd90291220d5a838536747a808a53ddf74e7f3e7))
* auto-delete branches after PR merge ([256af8e](https://github.com/genix-x/git-auto-flow/commit/256af8e84d9393a531d692f323c6d50928f6ffae))
* complete Git Flow installation with branch protection ([c31bf63](https://github.com/genix-x/git-auto-flow/commit/c31bf636a22cbbc5ea641e039b64643f747d12c8))
* create proper Git workflow with multi-AI ([951c96b](https://github.com/genix-x/git-auto-flow/commit/951c96b1ca1374bbea64f3d786adb974f0a17234))
* initial git-auto-flow package with multi-AI support ([caa2970](https://github.com/genix-x/git-auto-flow/commit/caa2970a982c41be8120b5bdebfe71fd6020fe53))
* **release:** add automatic version tagging and release workflow ([6347690](https://github.com/genix-x/git-auto-flow/commit/63476908c4fb5ae70a682e5a107595620651c7dc))
* update PR script to use multi-AI provider ([3441d02](https://github.com/genix-x/git-auto-flow/commit/3441d02410b61194dc95deefe00dca5ca32bc310))

# 1.0.0 (2025-08-22)


### Bug Fixes

* add package-lock.json for GitHub Actions ([c0a2a2d](https://github.com/genix-x/git-auto-flow/commit/c0a2a2dd937c828b369020ff75739d59210774f4))
* detect main branch if develop doesn't exist ([f0644a4](https://github.com/genix-x/git-auto-flow/commit/f0644a4a279a9bdb3d3ce264e07da92a77668114))
* remove invalid --delete-branch flag from gh pr create ([87accdb](https://github.com/genix-x/git-auto-flow/commit/87accdb9581d9e1ac479edff1431e89cb65a6717))
* switch to pnpm for semantic-release workflow ([78d3ebd](https://github.com/genix-x/git-auto-flow/commit/78d3ebd9b2aaea1791bc229c34cb0aee9b56b999))


### Features

* add semantic-release and interactive API key setup ([dd90291](https://github.com/genix-x/git-auto-flow/commit/dd90291220d5a838536747a808a53ddf74e7f3e7))
* auto-delete branches after PR merge ([256af8e](https://github.com/genix-x/git-auto-flow/commit/256af8e84d9393a531d692f323c6d50928f6ffae))
* complete Git Flow installation with branch protection ([c31bf63](https://github.com/genix-x/git-auto-flow/commit/c31bf636a22cbbc5ea641e039b64643f747d12c8))
* create proper Git workflow with multi-AI ([951c96b](https://github.com/genix-x/git-auto-flow/commit/951c96b1ca1374bbea64f3d786adb974f0a17234))
* initial git-auto-flow package with multi-AI support ([caa2970](https://github.com/genix-x/git-auto-flow/commit/caa2970a982c41be8120b5bdebfe71fd6020fe53))
* update PR script to use multi-AI provider ([3441d02](https://github.com/genix-x/git-auto-flow/commit/3441d02410b61194dc95deefe00dca5ca32bc310))
