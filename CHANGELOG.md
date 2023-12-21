# CHANGELOG



## v1.1.1 (2023-12-21)

### Fix

* fix: Removes versioning from appdirs (#26) ([`cfcf8e8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/cfcf8e8a3b4fa70fd5f518f92bf1866a7193b818))

* fix: Removes versioning from appdirs ([`1bedc79`](https://github.com/UCSD-E4E/e4e-deduplication/commit/1bedc798cdd8e28ebee16f619d1f9587bc80f916))


## v1.1.0 (2023-12-21)

### Feature

* feat: Adds list jobs ([`cbe46b8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/cbe46b867c8f23bf9f078e7fe1b72247b66ac629))


## v1.0.0 (2023-12-21)

### Breaking

* feat!: Switches cli to subcommands ([`3b8ccaa`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3b8ccaac6b9bff1bcbed9f1675d8f2728c3cb399))

* feat!: WIP -adding subcommands ([`02340be`](https://github.com/UCSD-E4E/e4e-deduplication/commit/02340bebe25d1380cb32c38390e3c7eadddb8b3d))

* feat!: Enables hostname aware comparison ([`55ea161`](https://github.com/UCSD-E4E/e4e-deduplication/commit/55ea1614c79ae13ea7641aeed9a3b6d7d6fc2a6c))

### Ci

* ci: Adds windows and macos for testing ([`568ce5a`](https://github.com/UCSD-E4E/e4e-deduplication/commit/568ce5a7a7aa37022f3bcfc04a55480c060f6775))

### Feature

* feat: allow for cross machine (#23) ([`3f6fa7b`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3f6fa7b937317a668acd5bc61f38a962de0ab481))

### Fix

* fix: Fixes *nix permissions ([`39b6c4d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/39b6c4da1bcff373ef5290baefd8e5b3cf1660f9))

* fix: Adds logging, fixes cache rebuild after cache sort ([`d200e15`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d200e1541edf79e561ee9a1ea5d042fcbc149f5e))

### Test

* test: Adds tests for os delete scripts ([`0745005`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0745005d2216f9adf55d79b01a17d2f88d647ee1))


## v0.7.1 (2023-12-18)

### Ci

* ci: Fixes env ([`43a3fa0`](https://github.com/UCSD-E4E/e4e-deduplication/commit/43a3fa03a3b180dd256ca146b2028486ccbea290))

* ci: Fixes poetry install ([`43c45bd`](https://github.com/UCSD-E4E/e4e-deduplication/commit/43c45bdb953aa62acf428215c8d82238edbb2b3c))

* ci: Fixes pytest execution ([`8ae5a2f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8ae5a2f1fce3a98542b97847b96713b670a1ecfb))

* ci: Adds nas_unzip ([`6537c11`](https://github.com/UCSD-E4E/e4e-deduplication/commit/6537c11814c92a1527a9af1df2ea35d2c7cd7b25))

* ci: adding support for nas unzip ([`2cc2509`](https://github.com/UCSD-E4E/e4e-deduplication/commit/2cc2509cb648d4e7eec18ec6ecf960d0733b0fb1))

### Fix

* fix: Faster job cache (#20) ([`a113912`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a1139127d8c405a788fa564de30bffb2c8657a10))

* fix: Fixes synology_api version ([`67e5d9d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/67e5d9dc9a5f46df5f1021af158a259bdff0f436))

* fix: switching to internal offset dict ([`00b02af`](https://github.com/UCSD-E4E/e4e-deduplication/commit/00b02af08576045d344a25b0a6026bf02250fa97))

### Style

* style: Fixes style ([`8e975e0`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8e975e0840d967084a90f8d9b670bfb8d94499bb))


## v0.7.0 (2023-12-17)

### Feature

* feat: Adds byte based progress bar (#18) ([`d8d2a07`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d8d2a0781e49526c0eeeddf259f17a1e2a91aa2b))

* feat: Adds byte based progress bar ([`27f9ec3`](https://github.com/UCSD-E4E/e4e-deduplication/commit/27f9ec317a519f020fc3bca3fc89109169f5dc69))


## v0.6.1 (2023-12-17)

### Fix

* fix: Fixes job cache handle initialization ([`ca3246d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ca3246d54db05cc8e31603a38fd13fe7364c3ea2))


## v0.6.0 (2023-12-16)

### Ci

* ci: Optimizes test ([`ef65ce1`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ef65ce194f41fcb9f3d535d339087802b50d497b))

* ci: Optimizes test fixture ([`80c9331`](https://github.com/UCSD-E4E/e4e-deduplication/commit/80c9331c785927aae4a3f113aa6f584915af2d38))

* ci: supporting testing ([`54f8ae8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/54f8ae8ec8d557bace56256b87f8baceb34b11ea))

### Feature

* feat: reduce sql db overhead (#17) ([`7200b03`](https://github.com/UCSD-E4E/e4e-deduplication/commit/7200b039a94787ea8044fa2c223cb4d656e90ca2))

* feat: Switch to csv based hash cache ([`b023e79`](https://github.com/UCSD-E4E/e4e-deduplication/commit/b023e79d6b000337a05432c1a576ae0ca35981e3))

### Fix

* fix: Fixes cache behavior ([`a9c4b3f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a9c4b3f097b093c2ea1891e480ccf537e9916800))

* fix: Removes extra prints ([`cdf08c4`](https://github.com/UCSD-E4E/e4e-deduplication/commit/cdf08c4de10652ddf3a76b7f6f2d84e920b281a9))

* fix: Implements file sorter ([`1b2132b`](https://github.com/UCSD-E4E/e4e-deduplication/commit/1b2132bddd719fae10b3641fda977baba0d167a5))

* fix: progress bar ([`fba9a28`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fba9a28fd7e7a85487efea3af0222fd0a9161094))

### Style

* style: Removes unused import ([`67fde55`](https://github.com/UCSD-E4E/e4e-deduplication/commit/67fde5521a1e5478a0dd63ab0d0007a79ca26480))

### Unknown

* wip: Switching to filesort based duplication ([`8820a1f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8820a1f74039e5f1b665cf513652204329327b78))


## v0.5.2 (2023-12-15)

### Fix

* fix: Switching to non-multiprocess Queue ([`f58cbaa`](https://github.com/UCSD-E4E/e4e-deduplication/commit/f58cbaacdaf17a76c3d8cf8e8b3990b0df2bfc60))

* fix: Removes submodule ([`9f0685d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/9f0685d7efad2b861389a79dd312a500d125ecae))


## v0.5.1 (2023-12-15)

### Ci

* ci: Fixes wheel build ([`0ba6a84`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0ba6a8406c8a4f74f6dca6afa61c546ef370ae74))

* ci: Fixes release.yml to no longer require cibuildwheel ([`fff48f6`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fff48f66e3b175d79a18470a454553535b1f00ef))

### Fix

* fix: Adds dynamic_ncols (#15) ([`e1a4bf3`](https://github.com/UCSD-E4E/e4e-deduplication/commit/e1a4bf30d20c516583992ae2ff8bd13dee57820f))

* fix: Adds dynamic_ncols ([`adf6529`](https://github.com/UCSD-E4E/e4e-deduplication/commit/adf65293b97656e4179e822e743c4aa148a4179e))


## v0.5.0 (2023-12-15)

### Feature

* feat: Uses python parallel hasher (#13) ([`c0351a5`](https://github.com/UCSD-E4E/e4e-deduplication/commit/c0351a51fdcfbe388a075137956ffa03d03f09c7))

* feat: Switching to python hasher ([`11b14ca`](https://github.com/UCSD-E4E/e4e-deduplication/commit/11b14ca5145a3e8caff37e1413fc5a2955d598fc))

* feat: Uses python parallel hasher ([`40a9eb1`](https://github.com/UCSD-E4E/e4e-deduplication/commit/40a9eb1bfc46c849fe0f94768d97187f71ab740e))

### Fix

* fix: Removes pybind11 dependency ([`7217838`](https://github.com/UCSD-E4E/e4e-deduplication/commit/7217838a3007d56a119eb591168d4655b70a8330))

### Style

* style: Refactors hash ([`5cd4ce9`](https://github.com/UCSD-E4E/e4e-deduplication/commit/5cd4ce9fc15791f91e4d32a67bf2ab0c7802e72c))


## v0.4.0 (2023-12-13)

### Feature

* feat: sqitches to sqlite3 and thread pool ([`1100593`](https://github.com/UCSD-E4E/e4e-deduplication/commit/1100593edba82b1306ce12260ec60dc1f7f59ff1))

* feat: Switches to a parallel thread hasher ([`ee04599`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ee04599928693f69bfb78ebc8461dc86dcd5b9eb))

* feat: Switching to threadpool and optimizing dataflow ([`998fb60`](https://github.com/UCSD-E4E/e4e-deduplication/commit/998fb6045fdcb90613953abe74dac7bd1a8c6690))

* feat: Implements sqlite3 backend ([`f87d9b8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/f87d9b820a03d00e6cc5be75fbf8b4d1a1e4e0ba))

### Fix

* fix: Fixes GIL release ([`acc71f1`](https://github.com/UCSD-E4E/e4e-deduplication/commit/acc71f17410b423b98445f3cc540a7ec96731422))

* fix: Re-adds the file discovery tqdm ([`6dcfc30`](https://github.com/UCSD-E4E/e4e-deduplication/commit/6dcfc30a6c097c0af1a26c1dc4babb4015f7b00c))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/sqlite3_testing&#39;

Conflicts:
	e4e_deduplication/analyzer.py ([`8c22f01`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8c22f011f780bfcf2102cad9441860b5cffbcd14))

* Merge branch &#39;master&#39; into 8-possible-memory-leak ([`15427e4`](https://github.com/UCSD-E4E/e4e-deduplication/commit/15427e44a25683ed0d8ecc1f5747a12c7883d918))


## v0.3.0 (2023-12-12)

### Feature

* feat: Adds progress bars

Merge pull request #11 from UCSD-E4E/4-progress-bar-for-analysis-result-aggregation ([`6abf954`](https://github.com/UCSD-E4E/e4e-deduplication/commit/6abf9541667df21de1ee0bc848aedf040616034e))

* feat: Adds progress bars ([`c45e590`](https://github.com/UCSD-E4E/e4e-deduplication/commit/c45e59037262e11d1ad26c8093b609d44853a6cb))

### Unknown

* Merge pull request #10 from UCSD-E4E/7-add-user-confirmation-for-clear_cache

feat: Adds clear cache check ([`8572e57`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8572e57aa3c72c0469000a655f19e59591fc2225))


## v0.2.2 (2023-12-11)

### Ci

* ci: Only build if released ([`fdd7a3f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fdd7a3f2ef46053227b06144d2efabf1fbe74609))

* ci: Fixes checkout ([`a1b0273`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a1b0273b024023c9a7b0f515aa809b61fc1d9fdd))

### Feature

* feat: Adds clear cache check ([`74d310b`](https://github.com/UCSD-E4E/e4e-deduplication/commit/74d310bcef4cfda6e5d6d252c477b136dc60dde8))

### Fix

* fix: Updates log timestamps ([`92514f6`](https://github.com/UCSD-E4E/e4e-deduplication/commit/92514f693e88b22494835d24a883f17521403341))

* fix: Fixes logging timestamp format ([`d518c7f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d518c7f22404029c1e029f56a902023ccfa947a0))


## v0.2.1 (2023-12-11)

### Ci

* ci: Adjusts release sequence ([`7509e85`](https://github.com/UCSD-E4E/e4e-deduplication/commit/7509e85624be4d5978c8c4949bfc611a4eee88cf))

* ci: Fixes release ([`2c07596`](https://github.com/UCSD-E4E/e4e-deduplication/commit/2c07596e995a4be6b892e174b59cb72bbc64c3b0))

### Documentation

* docs: Fixes readme ([`495789d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/495789d33a416750747b7cd5dcbd82d91d96f752))

### Fix

* fix: Fixes naive job file

Merge pull request #3 from UCSD-E4E/naive_job_file ([`a9e57fb`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a9e57fb3ea3a2101faa65cfeeb996b82362e922e))

* fix: Allows for empty dict in job cache ([`98dfd56`](https://github.com/UCSD-E4E/e4e-deduplication/commit/98dfd56b139e41e4d9848d18670b0325e57a3219))

### Style

* style: Fixes docstring ([`e0f8192`](https://github.com/UCSD-E4E/e4e-deduplication/commit/e0f819242e8ce95a8c52d366eb8fec990d082b49))


## v0.2.0 (2023-12-11)

### Feature

* feat: Updates dedup for synology

Merge pull request #2 from UCSD-E4E/file_filter ([`404641f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/404641fccb68b37bddbbde4f653b89f720dd8d6c))

* feat: Updates dedup for synology ([`b14f926`](https://github.com/UCSD-E4E/e4e-deduplication/commit/b14f926cf0ff56cecd0dc66f34a0f948f26ab74e))


## v0.1.2 (2023-12-11)

### Fix

* fix: Reduces console output to WARNING instead of DEBUG ([`fcfbe79`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fcfbe7928fa466d94fbc897a01dc16a1e375d392))

### Unknown

* Merge branch &#39;master&#39; of github.com:UCSD-E4E/e4e-deduplication ([`f9cd7a5`](https://github.com/UCSD-E4E/e4e-deduplication/commit/f9cd7a535849e33c20b1e3b39dc11b14c9ecccaf))


## v0.1.1 (2023-12-11)

### Fix

* fix: Fixes release publish ([`81bc878`](https://github.com/UCSD-E4E/e4e-deduplication/commit/81bc878ff37d6d549bfe12197e0360e3ee69bc7a))


## v0.1.0 (2023-12-11)

### Ci

* ci: Fixes branch name ([`22aae2c`](https://github.com/UCSD-E4E/e4e-deduplication/commit/22aae2c9d3dddf613933d1171aed5117cdcace29))

* ci: Logging timing errors instead ([`82e967a`](https://github.com/UCSD-E4E/e4e-deduplication/commit/82e967a8f9f8b388407980a73c50d41db99553b1))

* ci: Reduces mutiproc to 128MB ([`f3f995c`](https://github.com/UCSD-E4E/e4e-deduplication/commit/f3f995c2cbbadf419e3b81c3cfff4b5f23721759))

* ci: Adds pytest for import ([`666c7a9`](https://github.com/UCSD-E4E/e4e-deduplication/commit/666c7a91baa62cadaaff566fa845fabf2eaaac74))

* ci: Switching to pip install ([`474808f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/474808f5db4eb0695ab0346e5e270f9fbbe7b249))

* ci: uses poetry to execute ([`903b93a`](https://github.com/UCSD-E4E/e4e-deduplication/commit/903b93ad7eb390d43b10d5dbf1bb32ba5d719325))

* ci: Adds coverage ([`13174d8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/13174d8da97b92c7cafcee7d4d3f3ad0c4569882))

* ci: Disables venv ([`535708c`](https://github.com/UCSD-E4E/e4e-deduplication/commit/535708ceb0d10da4cf2bf6d276097d70c9327945))

* ci: Fixes install ([`c2d9f3c`](https://github.com/UCSD-E4E/e4e-deduplication/commit/c2d9f3c4bae6c12261201279f64415dc62c576ac))

* ci: Fixes checkout ([`4511bc1`](https://github.com/UCSD-E4E/e4e-deduplication/commit/4511bc1804de1c3baa9487adc78bccbe82c366ee))

* ci: Updates lock file ([`3bccb81`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3bccb81627a102c7df36be1b0d37fe5a4a628663))

* ci: Adds -v to poetry install for debug ([`bdee9cf`](https://github.com/UCSD-E4E/e4e-deduplication/commit/bdee9cfebcc503b01d6cb67c633c5ea5affa73dd))

* ci: Fixes pylint ([`b6a1b85`](https://github.com/UCSD-E4E/e4e-deduplication/commit/b6a1b85c5fc3098c3bd2dc4083ef0d6f5d85289c))

### Documentation

* docs: Adds badges ([`fffe499`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fffe499e1e0a74f8be031d3a5ded2494576dbb79))

* docs: Updates readme ([`ef3ab3e`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ef3ab3ea89248fda5eb93181dd0544cfed06e053))

### Feature

* feat: Merges pyFileHash for wheel ([`5325524`](https://github.com/UCSD-E4E/e4e-deduplication/commit/532552484dcee19c5908c32566bf497eb310a5e3))

* feat: Adds progress bar for file discovery ([`0e3c773`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0e3c773840dc7d013a61ee991f23fc7de7fef97c))

* feat: Adds report ([`d1b74a2`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d1b74a2e147b47bc5de3223444f330a1c415c158))

* feat: Updates behavior ([`e3cec29`](https://github.com/UCSD-E4E/e4e-deduplication/commit/e3cec29d251c87f3dde23b2181d6b9245f73e291))

### Fix

* fix: Fixes tests ([`a1e0b12`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a1e0b12aee51662c5c21b3cb87e391ba2593e0af))

### Style

* style: Linting ([`b013cbb`](https://github.com/UCSD-E4E/e4e-deduplication/commit/b013cbbd8d82b2d4e1cf5adc43ec73cb6f2558db))

* style: Linting ([`53d0df6`](https://github.com/UCSD-E4E/e4e-deduplication/commit/53d0df6ca654f5e2e8d18f9bc1383f778bd228b5))

### Unknown

* Merge pull request #1 from UCSD-E4E/gh_actions

Github Actions ([`69bfb16`](https://github.com/UCSD-E4E/e4e-deduplication/commit/69bfb16f614df1c1d3a8d30492b65cf561537c59))

* add missing parameter to report.generate ([`3cda02b`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3cda02bbfbeb96353dd77d5526f31fb825452647))

* handle root path ([`5ada477`](https://github.com/UCSD-E4E/e4e-deduplication/commit/5ada477e9dc74e6f9c9a3e1aa0494fa7ec7062c8))

* fix bug with logging parameters ([`a22e206`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a22e20684ba5490cb39c5e1cac68b29da3bab3a8))

* support providing original paths ([`4ecfd10`](https://github.com/UCSD-E4E/e4e-deduplication/commit/4ecfd10c3002971e89a0e27bb147202ed9832566))

* remove printing that checksums are being calculated ([`774e82d`](https://github.com/UCSD-E4E/e4e-deduplication/commit/774e82d6185ffa4ec44d9063a8c3d77bcd3b08d4))

* unpack mtime as a tuple from sqlite to address bug causing checksums to be recalculated for all files ([`3cf892b`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3cf892b4940c96f73f23cc652a7f47c29ab1e1d0))

* print mtime of both files ([`0a27b16`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0a27b164bf8eb0c66601e8d5cfb5c177d17a4c40))

* print when we are running checksum ([`a1050bd`](https://github.com/UCSD-E4E/e4e-deduplication/commit/a1050bdd4f2932ae3964844a5e31ab4f2335ea0a))

* always update seen, even if mtime is the same ([`e018423`](https://github.com/UCSD-E4E/e4e-deduplication/commit/e018423a8dec8539ed487bdb0c6d64be35cc78ab))

* always print file, even if in cache ([`8698499`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8698499174550e9da21a0cb1725e92ac2effd8b4))

* better handle excluded paths ([`beee5bf`](https://github.com/UCSD-E4E/e4e-deduplication/commit/beee5bfda81dea95ceb13e22c5097bead69aa0d9))

* reintroduce the in memory cache ([`c5379a2`](https://github.com/UCSD-E4E/e4e-deduplication/commit/c5379a2c83c1c392e7519f2d92d03a6ae33c226e))

* fix no such column seen error ([`74c593e`](https://github.com/UCSD-E4E/e4e-deduplication/commit/74c593ea071b58ae24fcbc722912f165d350bfd8))

* support rechecking files already in cache ([`381c3d9`](https://github.com/UCSD-E4E/e4e-deduplication/commit/381c3d92b0648302ae3fb5a44b23957dbd3f81bc))

* simplify dirty check for cache ([`ee6f535`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ee6f535845f52220418019c3ca9a447cc5132ffd))

* handle only updating the db if cache is dirty ([`4d09bee`](https://github.com/UCSD-E4E/e4e-deduplication/commit/4d09bee1f9285a53de617cbcdc014acf9c06f408))

* support in memory caching to speed up processing ([`d367850`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d367850b066317e95d05b62a086927ff81f3c00d))

* correctly check to see if RootDir is in the db ([`bc3bfcc`](https://github.com/UCSD-E4E/e4e-deduplication/commit/bc3bfccce95b6fa240bb4a523dfbc0dc59e5722d))

* cast cursor to list ([`1a352b9`](https://github.com/UCSD-E4E/e4e-deduplication/commit/1a352b922fb03319b7a9b9e50a7e5ad01d848cbf))

* handle pulling the metadata correctly ([`cb292d8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/cb292d8a602ed188ae3283e7ef496cf28cca7d80))

* don&#39;t print path if already in cache ([`c69d95e`](https://github.com/UCSD-E4E/e4e-deduplication/commit/c69d95e258c466c64366bcde32460ad52572a0d8))

* comment the code ([`292aa68`](https://github.com/UCSD-E4E/e4e-deduplication/commit/292aa68cc310bd409c0e0c1a86de2cfa83b6e715))

* correct pylint errors ([`098f68f`](https://github.com/UCSD-E4E/e4e-deduplication/commit/098f68fa8ffa95d5fcc5dbfb5739d046409fb155))

* use home directory from pathlib ([`3c36dd8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3c36dd8546c697e12442b6923f8c46631c9d1de8))

* support older version of python ([`7479acd`](https://github.com/UCSD-E4E/e4e-deduplication/commit/7479acd1b860fa3b3774a8f1fd4fbb999293cb21))

* only copy to nas when complete ([`3d7eced`](https://github.com/UCSD-E4E/e4e-deduplication/commit/3d7eced146c896226900fd220dc3aefd8853c59d))

* commit every 10 items or every 10 minutes.  whichever comes first. ([`0fea6ec`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0fea6ec7d098d7d3204012775a37cc8c490a1d16))

* instead of committing every 10 items, commit every 10 minutes. ([`2c118ce`](https://github.com/UCSD-E4E/e4e-deduplication/commit/2c118ce0ede54696c4326a9d625bc45129e6553f))

* update cache to handle renames ([`aa757ea`](https://github.com/UCSD-E4E/e4e-deduplication/commit/aa757eab39a7aadd759012164024b55185ead39c))

* only delete cache file if exists ([`29ccaa8`](https://github.com/UCSD-E4E/e4e-deduplication/commit/29ccaa8a582459fb8f59b6b6ff8ebd2334db8160))

* revert back to sha256 instead of file_digest to support older versions of python. ([`1558466`](https://github.com/UCSD-E4E/e4e-deduplication/commit/15584669eda60757994c14b3453cd3412748e7b4))

* revert back to sha256 instead of file_digest to support older versions of python. ([`d898021`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d8980214564d1ce6b53b90690120b0a86d075a32))

* fixed bug in cache object with-statement ([`d3495a5`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d3495a538c9f2216f9c6d556da0fd41ebb6e2d18))

* excluded files in Directory object ([`ce60432`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ce60432b284f841705b7e63ad8b8a3ff940f69a4))

* support excluded files ([`6b090e3`](https://github.com/UCSD-E4E/e4e-deduplication/commit/6b090e34aeaaa6c3707b2077f524d8dfd52bc69f))

* commit to cache every 10 items ([`ed66f63`](https://github.com/UCSD-E4E/e4e-deduplication/commit/ed66f63799138e4c2dcd6dc184843683360b055b))

* support cache with-statement.  Store cache in local folder ([`8df8853`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8df885312e8af84734339efc5e2d6a5a8fbfab99))

* reverse previous commit.  add some missing type hints ([`8b061f5`](https://github.com/UCSD-E4E/e4e-deduplication/commit/8b061f5a9e5a50b68d09011f8c1a4f86b9955d85))

* always commit after adding file ([`20355eb`](https://github.com/UCSD-E4E/e4e-deduplication/commit/20355eb42bdf603fcfa0dfb6b2c71a32a46044fb))

* print out current file name ([`6028958`](https://github.com/UCSD-E4E/e4e-deduplication/commit/602895875942d5f473b01c38ef2a10cc1e3eb821))

* move black and pylint to dev dependencies ([`f6061e4`](https://github.com/UCSD-E4E/e4e-deduplication/commit/f6061e44d95c204d7b3b6e61d8f252e20a554016))

* move pylint and black to dev dependencies ([`0fb7d20`](https://github.com/UCSD-E4E/e4e-deduplication/commit/0fb7d20ff2193bb06ebfc4dca0f8dcb8d4ac3267))

* fix pylint errors ([`d2474b1`](https://github.com/UCSD-E4E/e4e-deduplication/commit/d2474b10ef73f05efde8d5b7dd2108f944977549))

* update cache to no longer use hard coded &#39;/&#39; and use file_digest to compute hash ([`fdb7f29`](https://github.com/UCSD-E4E/e4e-deduplication/commit/fdb7f299b0ef78cbd6d086d0fb85b6b5944ad998))

* address Nathan&#39;s comments ([`bdf88ca`](https://github.com/UCSD-E4E/e4e-deduplication/commit/bdf88ca94389fe5b50c216c1c3c1976b8a4942af))

* initial checkin of the e4e deduplication tool. ([`e1d9c35`](https://github.com/UCSD-E4E/e4e-deduplication/commit/e1d9c35d3fd1c4c402c2ece419917568b8b4901a))
