# Spec: the portable avd-assess map

> Personal project. Research and learning only, not for production, provided as is. Not affiliated with, endorsed by or supported by the author's employer, Liquidware or Microsoft. Azure Virtual Desktop is a trademark of its owner.

- **Status:** draft, red-teamed by Fable (section 15, 15 findings, all fixed), nothing built. No release is cut and no consumer changes until the owner says go; the owner tags releases from Cloud Shell.
- **Date:** 2026-10-21
- **Owner's ask (2026-10-21):** "our avd-assess map should be portable/distributable too." Anyone, inside the family or not, should be able to take the map at a version, check it is what avd-assess published, and use it offline.
- **Builds on:** [contracts/README.md](../contracts/README.md) (byte-identical vendoring, fail-open rules), avd-ops [decision 0008](https://github.com/avd-ops/avd-ops/blob/main/docs/knowledge/decisions/0008-code-signing.md) (immutable releases and attestations for every repo, $0), the map (section 0 of [assess-spec.md](assess-spec.md)).

## 1. Summary

avd-assess publishes its map as a **versioned release bundle**: the JSON documents readers already use (`index.json`, `method.json`, `map.json`, the fact register, the security review map, `endpoints.json` from PR #39), their JSON Schemas, a [Frictionless Data Package](https://datapackage.org/) manifest (`datapackage.json`) with a SHA-256 per file, and a `SHA256SUMS` file. Every file in a release is byte-identical to the same path in git at the tagged commit, so today's commit pins stay valid and a release pin is a commit pin with a hash list on top. Releases are immutable GitHub releases with build provenance attestations. GitHub Pages carries a catalog, the schemas at stable `$id` URLs and a convenience mirror, never trusted without the hash. A tiny verifier (Python standard library, and a PowerShell module that runs on 5.1 and 7) checks a vendored copy against its pin. Consumers keep vendoring; nothing fetches at run time; versions follow semantic versioning, and a release workflow refuses a tag whose bump is smaller than the change.

## 2. What exists today

| Piece | Today | Gap for an outside reader |
|---|---|---|
| Documents | `index.json` (C20 `avd-assess-index/v1`, 390 KB), `method.json` (`avd-assess-method/v1`, own integer `version` 3), `map.json` (`avd-assess-map/v1`, 240 KB), `contracts/fact-register.json` (C15, own `version` 1), `contracts/run-use-cases.json`; `security-review.json` in PR #38; an endpoint map in progress | No version of the whole; a reader can't tell which documents belong together except by commit |
| Generation | `scripts/build_index.py` builds `index.json` and `map.json` from YAML; CI `--check` fails when stale | None; this stays |
| Schemas | `contracts/schemas/*.json`, JSON Schema 2020-12, no `$id` (only `evidence/schema.json` has one, still on the old owner, PR #37) | No stable URL to resolve or cite a schema by |
| Consumers | avd-current-state `assess/PINS.json` (2 files) and `contracts/PINS.json` (5) at `a5f4df1`; avd-landing-zone `contracts/PINS.json` (6 files at `b4209a7`, plus C14 from the brain); avd-second-brain `contracts/FOUNDATION-PINS.json` (20 files at `ac7751d`); the avd-ops security page (PR #30) reads the security review map | Three PINS.json shapes; each consumer writes its own hash test; each copies files by hand |
| Tags and releases | None in avd-assess | No way to pin "a release", no provenance |
| License | MIT; references link to and pin upstream pages, claims are one line in our words | No machine-readable license or attribution with the data |

## 3. Prior art

Searched 2026-10-21 (the family's `prior_art.py` could not reach GitHub search from the container; web search and the sources' own docs instead). The rule is the family's build-or-adopt: adopt only what is the best at the job and open source.

| Prior art | How it distributes data | Verdict |
|---|---|---|
| [Frictionless Data Package v2](https://datapackage.org/standard/data-package/) (June 2024; spec released into the public domain) | A `datapackage.json` descriptor listing each resource's `path`, `bytes`, `hash` (`sha256:` prefix allowed), `licenses`, `sources` and a `version`; descriptors may carry extra properties | **Adopt** as the manifest format. It is the open standard for describing a bundle of data files, has validators in several languages, and needs no tool of ours to read. We use a small subset and add one property (`jsonSchema`) |
| [Terraform provider releases](https://developer.hashicorp.com/terraform/registry/providers/publishing) and the dependency lock file | Release assets plus `SHA256SUMS` and a GPG signature; the consumer's lock file records the hashes it accepted | **Borrow** `SHA256SUMS` (checkable with `sha256sum -c` anywhere) and the lock-file idea, which our `PINS.json` already is. **Reject** GPG: decision 0008 refused long-lived signing keys |
| [OSV](https://google.github.io/osv.dev/data/) | One JSON per record with a `schema_version`, plus `all.zip` per ecosystem, in a bucket that always holds the latest | **Borrow** a schema string in every document (we have `schema`). **Reject** latest-only: a reader can't pin it |
| [MITRE ATT&CK attack-stix-data](https://github.com/mitre-attack/attack-stix-data) | Version-named files (`enterprise-attack-20.0.json`) and a floating latest file in git, plus a machine-readable `index.json` listing every version with its URL | **Borrow** the catalog (our Pages `catalog.json`, section 5). Its index carries no hashes; ours does |
| [SchemaStore](https://www.schemastore.org/) | A catalog of schema URLs that editors resolve by `$id` | **Borrow** stable `$id` URLs. Listing there waits for outside demand (open question 7) |
| [CycloneDX specification](https://github.com/CycloneDX/specification) | Versioned schema files, the version in the file name and `$id`, released by tag | **Borrow** the major version in each schema's `$id` |
| [OpenSSF Scorecard](https://github.com/ossf/scorecard) | Results through an API and a public dataset, signed with Sigstore | **Borrow** Sigstore provenance, which GitHub attestations give us. **Reject** a run-time API: the foundation never fetches |
| [GitHub immutable releases and attestations](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verifying-the-integrity-of-a-release) | Assets and tag locked once published; a release attestation in Sigstore format; `gh release verify`, `gh release verify-asset`, `gh attestation verify` | **Adopt**, as decision 0008 already chose for the family |
| OCI artifacts in a container registry; npm or PyPI packages | Content-addressed artifacts; language package managers | **Reject for now:** a registry client or a publish credential that most readers (Cloud Shell, a static page, a PowerShell script) don't need. Open question 6 |

## 4. The bundle

### 4.1 What is in it

Everything a reader needs to use the map without cloning, at the repo paths it has in git:

| Path | Kind | Notes |
|---|---|---|
| `index.json`, `method.json`, `map.json` | documents | C20 |
| `security-review.json` | document | when PR #38 merges |
| `endpoints.json` | document | `avd-assess-endpoints/v1`, schema `contracts/schemas/assess-endpoints.schema.json`, when PR #39 merges (section 11) |
| `contracts/fact-register.json`, `contracts/run-use-cases.json` | documents | C15, C17 |
| `contracts/schemas/*.json`, `evidence/schema.json` | schemas | the schema of every document that has one, so a reader can validate what it holds (`run-use-cases.json` has none today; its resource carries no `jsonSchema` and the verifier reports it as not schema-checked) |
| `contracts/examples/**` | examples | the brain vendors them today; `.jsonl` examples are `format: jsonl` and parsed line by line |
| `methods/*.md`, `gaps/*.md`, `contracts/README.md`, `README.md`, `LICENSE`, `NOTICE` | text | the method a person reads; small |
| `tools/avd_assess_bundle.py`, `tools/AvdAssessBundle.psm1`, `tools/diff_bundle.py` | verifier and diff | sections 6 and 8; vendored by consumers like any other file |
| `datapackage.json`, `SHA256SUMS` | manifest | generated at release, not in git (4.3) |

Not in it: the YAML sources (`dimensions.yaml` and the rest stay the authority in git; the JSON is their published view, which is why `build_index.py` exists), tests, CI, and anything not tracked in git.

**Byte identity.** The release workflow builds the bundle from the tag's tree, file by file (`git ls-tree -r <tag>` and `git cat-file blob <tag>:<path>`), never from a working tree or `git archive`, because `git archive` applies `core.autocrlf`, `eol` and `export-subst` and `export-ignore` attributes and would change bytes or membership. Every file's bytes therefore equal its git blob, and a test fails if `.gitattributes` ever gains an `eol`, `text` or `export-*` attribute for a bundled path. A consumer pinned to the tag's commit already holds the right hashes. Consumers on Windows keep vendored folders out of line-ending conversion with a `.gitattributes` line (`contracts/** -text`), as the cross-platform CI already needs.

### 4.2 The manifest: `datapackage.json`

A Data Package v2 descriptor, generated by `scripts/bundle/build_bundle.py`:

```json
{
  "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
  "name": "avd-assess",
  "title": "avd-assess: the AVD assessment map",
  "version": "1.0.0",
  "created": "<the tagged commit's date, git log -1 --format=%cI>",
  "homepage": "https://github.com/avd-ops/avd-assess",
  "description": "Personal project, not for production, as is; not affiliated with the author's employer, Liquidware or Microsoft.",
  "licenses": [{ "name": "MIT", "path": "LICENSE" }],
  "sources": [{ "title": "Microsoft Learn and the other pinned references in index.json, linked, never copied", "path": "NOTICE" }],
  "avdAssess": { "commit": "<40-hex commit of the tag>", "tag": "v1.0.0", "profile": "avd-assess-bundle/v1" },
  "resources": [
    {
      "name": "map",
      "path": "map.json",
      "format": "json",
      "mediatype": "application/json",
      "bytes": 238926,
      "hash": "sha256:<64 hex>",
      "schemaString": "avd-assess-map/v1",
      "jsonSchema": "contracts/schemas/assess-map.schema.json"
    }
  ]
}
```

- The generator is deterministic: `created` is the tagged commit's date, resources are sorted by path, keys are written in a fixed order, so anyone can rebuild `datapackage.json` from the tag and get the same bytes (a CI test runs it twice and compares).
- One resource per file in 4.1 except the manifest itself and `SHA256SUMS`. `name` is unique, lower case (`map`, `method`, `index`, `fact-register`, `schema-assess-map`, `method-security`, ...).
- `hash` always `sha256:`; `bytes` always present. A resource with a top-level `schema` string in its content repeats it as `schemaString` and names its schema file in `jsonSchema`; readers choose what they need from the manifest alone. A document resource also lists `idPaths`, the JSON pointers to its ID fields (for `map.json`: `/pillars/*/id`, `/dimensions/*/id`, ...), (RFC 6901 pointers extended with one rule: a `*` segment matches every item of an array), so `diff_bundle.py` (section 6) can compare ID sets for any document, including ones added later, without code of its own for each.
- `avdAssess` holds what Data Package has no field for. `avd-assess-bundle/v1` is the profile in 4.4.
- The manifest is pinned by its own SHA-256 in each consumer's `PINS.json`; that one hash pins every file (section 9).

`SHA256SUMS` lists the same files in the `sha256sum` format (`<hash>  <path>`), sorted by path, for people who check by hand.

### 4.3 Why the manifest is not in git

It holds a hash of every file, so committing it would make every pull request that touches any file conflict on it; the pillar threads run in parallel. It is generated at release from the tag, and CI on every pull request runs the generator in a dry run so a broken bundle fails before a tag ever does.

### 4.4 The bundle profile, `avd-assess-bundle/v1`

A JSON Schema in `contracts/schemas/assess-bundle.schema.json` (new, additive) for the manifest: Data Package required fields as above, `hash` matching `^sha256:[0-9a-f]{64}$`, `bytes` an integer, `avdAssess.commit` 40 hex, `version` semantic, paths relative with no `..`, no leading `/` and no backslash, names unique. The verifier checks it with no schema library (section 8).

### 4.5 Release assets

| Asset | Why |
|---|---|
| `avd-assess-<version>.zip` | the whole bundle; entries sorted, fixed timestamps |
| `datapackage.json`, `SHA256SUMS` | the pin and the human check |
| each JSON file whose base name is unique (`map.json`, `fact-register.json`, `assess-map.schema.json`, ...) | a reader that wants one document doesn't unzip; the workflow fails on a duplicate base name |

Every asset gets a build provenance attestation (`actions/attest-build-provenance`), and the immutable release gets GitHub's release attestation. GitHub's automatic "Source code" archives are not the bundle: they are made on demand, `gh release verify-asset` can't check them, and `git archive` rules apply to them. Readers use `avd-assess-<version>.zip`.

## 5. Where it lives

| URL | Mutable | Use |
|---|---|---|
| `https://github.com/avd-ops/avd-assess/releases/download/v<version>/<asset>` | no (immutable release) | the canonical copy; what a consumer downloads at re-pin |
| `https://github.com/avd-ops/avd-assess/releases/latest/download/<asset>` | yes | people only; nothing pins it |
| `https://assess.avd-ops.dev/catalog.json` | yes | every release: version, tag, commit, date, manifest SHA-256, asset URLs, and which documents changed major |
| `https://assess.avd-ops.dev/schemas/<schema-name>/v<major>.json` | yes, within a major | each schema's `$id`; holds the newest minor of that major, which is backward compatible by section 6 |
| `https://assess.avd-ops.dev/v/<version>/<path>` | Pages can change | a mirror for browser tools: GitHub Pages answers cross-origin requests and release downloads may not (assumption to verify in phase 1); every reader still checks the manifest hash |

Pages is published by a `pages` job inside `release.yml` that runs after the publish job (a release published with the workflow's own token starts no other workflow, so a separate `release: published` trigger would never fire), and by `workflow_dispatch` to rerun it if a deploy fails after publishing. It builds from release assets only, never from a working tree. A Pages page is a convenience, never a trust anchor: section 9's pins are hashes, so a changed mirror fails the check.

**Schema `$id`.** Phase 1 gives every schema an `$id` of the form above (`https://assess.avd-ops.dev/schemas/avd-assess-map/v1.json`). Adding `$id` changes the schemas' bytes, so consumers pick it up at their next re-pin; nothing breaks before that, because pins name a commit. `$id` is an identifier: no reader resolves it over the network.

## 6. Versioning

One semantic version for the whole bundle, `MAJOR.MINOR.PATCH`, starting at `1.0.0` (the contracts are already v1 and in use). Each document keeps its own `schema` string (`avd-assess-map/v1`), whose major moves only with a breaking change to that document; `method.json` and the fact register keep their own integer `version` as they do today. The bundle major is the highest-impact change in any document.

**The test for "breaking":** a reader written for the previous release, following the contracts' reader rules (ignore unknown fields and values, accept a newer minor), now fails, misreads, or loses a citation it holds.

| Bump | When |
|---|---|
| **MAJOR** | a document's `schema` major bumps (a required field added, a field removed or renamed, a type or pattern changed, since a diff can't tell narrowing from widening, unless the release PR shows it only widens; an enum value removed); a document removed or renamed; any ID removed or renamed (pillar, dimension, reference, claim, observation, gap, check, fact, use case, gold standard, endpoint row); a fact renamed or removed (the register's own `version` bumps too, contracts rule 6); a field or ID keeps its name but changes meaning or unit |
| **MINOR** | a new document, ID, optional field or enum value; a deprecation mark; any `method.json` change (new check, threshold, `onFail`), with its own `version` bump and a release note line "method changed: scores can move"; a pin moved and the claim's words changed |
| **PATCH** | a pin refreshed with the same claim; wording in our own text, method or gap pages; metadata; no ID, field or method change |

**Deprecation before removal.** Removing an ID is always a major. Before it, the ID gets `deprecated: { "since": "<version>", "replacedBy": "<id or null>" }` (an optional field, added to each schema in phase 1), which is a minor. The deprecation window is a gate, not a bump modifier: the release workflow refuses a major that removes an ID unless that ID carried `deprecated` in the documents of a published release at least 30 days earlier (the dates from `gh release list`, the marks from that release's bundle). Citations keep resolving through the window.

**The bump is computed where it can be, declared where it can't.** `scripts/bundle/diff_bundle.py <old release dir> <new release dir>` compares two full bundles and computes: the file set; each document's `schema` string; each schema's `required`, `type`, `enum` and `pattern` keywords (added required, removed enum value, changed type or pattern: major, which the release PR may lower to minor with a `NOT-BREAKING:` line saying why the change only widens, for the owner to accept at the gate); ID sets from each resource's `idPaths` (removed: major, added: minor); `deprecated` marks; the register's facts and `version`; `method.json`'s `version`; and, per reference claim, whether `says` changed with its pin (minor) or only the pin moved (patch). It prints the smallest allowed bump with its reasons. What a diff cannot see, a field or ID that keeps its name but changes meaning or unit, the release PR declares in a `BREAKING:` line; the workflow takes the larger of the computed and the declared bump (after any accepted `NOT-BREAKING:`) and fails a tag below it. The output becomes the release notes under "Breaking", "Method" and "Added".

## 7. Release process

1. **Release PR** (a session may open it): runs `diff_bundle.py` against the last release and states the version and the notes. No version file to edit; the tag carries it.
2. **The owner tags** from Cloud Shell after merging, with a block like:

   ```powershell
   if (Test-Path ~/avd-assess) { git -C ~/avd-assess pull --ff-only } else { git clone https://github.com/avd-ops/avd-assess ~/avd-assess }
   Set-Location ~/avd-assess
   git tag -a v1.0.0 -m "avd-assess 1.0.0" origin/main
   git push origin v1.0.0
   ```

   A Claude session never pushes a tag (CLAUDE.md gets that rule in phase 1).
3. **Who can tag.** A repository ruleset lets only the owner create `v*` tags (free on public repositories); a check in the workflow that the tag is on `main` is kept as a guard against mistakes, not as a control, because the workflow file at the tag is the tag author's.
4. **`.github/workflows/release.yml`** on the tag push: refuses a tag that isn't `v<semver>` or isn't on `main`; runs every check in `check.yml` at the tag; builds the bundle from the tag's blobs (4.1) and writes `datapackage.json` and `SHA256SUMS`; runs `diff_bundle.py` between the previous release's bundle (downloaded from its immutable release) and the new one and enforces the bump and the deprecation gate (for the first release there is no previous one: both gates are skipped and the notes say "first release"); runs the leak scan (GUIDs not in `tests/public-ids.txt`, emails, IPv4 addresses not on the repo's allowlist of published Microsoft addresses that the endpoint map needs, non-ASCII, the wording list) over every file in it; verifies the result with both verifiers; attests every asset; creates a **draft** release with the assets, then publishes it (immutable releases lock a release when it is published, so assets go up first). The job runs in a `release` environment whose required reviewer is the owner, so a pushed tag alone publishes nothing. Permissions: `contents: write`, `id-token: write`, `attestations: write`; no secret; every action pinned by commit SHA. The owner both pushes the tag and approves the environment; with one maintainer that is deliberate, and the gate's value is that nothing publishes without a person looking at the computed notes.
5. **Pages** (the `pages` job) deploys `catalog.json`, the schemas and the mirror from the published release.

**When a step fails.** Before publish: the job leaves a draft release; the owner deletes the draft and the tag (an unpublished tag is still deletable), fixes, and tags again. After publish: the release is permanent; a failed Pages job is rerun with `workflow_dispatch`, and nothing a consumer needs depends on Pages.

A bad release is never replaced: it is marked withdrawn in `catalog.json` (`"withdrawn": "<reason>"`), in its own release notes if GitHub still allows editing them (to verify in phase 1), and in the notes of the fixed release that follows, so a consumer without Pages still sees it. Immutable releases make the tag and assets permanent once published, which is the point.

## 8. Reader and verifier

Two implementations of one check, each one file, shipped in the bundle under `tools/` and tested against the same fixtures (`tests/fixtures/bundle/`: a good bundle, a changed byte, a missing file, a manifest with a bad hash, a path with `..`, an unknown schema major, a schema-invalid document).

- `tools/avd_assess_bundle.py`: Python 3.9+, standard library only (`hashlib`, `json`, `pathlib`). Schema validation uses `jsonschema` when it is installed and says "schemas not checked" when it isn't.
- `tools/AvdAssessBundle.psm1`: one pure function, `Get-AvdAssessBundleCheck -Path <dir> [-ManifestSha256 <hex>] [-Resource <names>] [-PathMap <hashtable>] [-KnownSchema <strings>]`, that emits one result item per check (`id`, `status` PASS/WARN/FAIL, `detail`), the family's check-item shape. Hashes with .NET's SHA-256, so it runs on Windows PowerShell 5.1 and PowerShell 7 on any OS. Schema validation runs only on PowerShell 7.4 or later (`Test-Json -Schema`), otherwise WARN.

**Consumers keep their own layout.** avd-current-state holds `method.json` as `assess/method.json`, and the brain keeps its files under `contracts/`. Both verifiers take a path map (bundle path to local path), which a consumer builds from its `PINS.json` `files` keys and its vendored folder, so nobody has to mirror the bundle's tree.

What both check, in order, stopping at the first FAIL:

1. the manifest's SHA-256 equals the pin, when one is given;
2. the manifest matches the bundle profile (4.4), with no library;
3. each wanted resource (all, by default) exists, has its `bytes`, and its SHA-256 matches;
4. each wanted JSON resource parses, its top-level `schema` equals `schemaString`, and that string's major is one the caller knows (an unknown major is FAIL for the verifier; how the consumer treats it is the consumer's rule, below);
5. each wanted JSON resource validates against its `jsonSchema` when a validator is available.

Output lines are `RESULT PASS|WARN|FAIL <detail>`; exit 0 all passed, 2 passed with schemas not checked, 1 failed. Neither tool touches the network.

**What a failed check means to each reader** is set by that reader, following the contracts' rules:

| Reader | Bundle missing, invalid or an unknown major |
|---|---|
| avd-current-state (runs `method.json`) | fails open: the inventory and validator run, the assess step is skipped with a WARN naming the check; `-Strict` makes it an error |
| avd-landing-zone (reads the register and run schemas) | caught in CI at re-pin, where its tests run the verifier; at run time the files are in git |
| avd-second-brain, avd-swarm | the guidance is dropped with a warning |
| avd-linecheck and portals reading the endpoint map | **fail closed** on verdicts: no probe list means "not tested", never a pass (its rule L3) |

## 9. Pinning and re-pinning

A consumer's `PINS.json` keeps the fields it has and adds two:

```json
{
  "source": "https://github.com/avd-ops/avd-assess",
  "commit": "<40-hex commit of the tag>",
  "release": "v1.0.0",
  "manifest": "<sha256 of datapackage.json>",
  "files": { "map.json": "<sha256>", "contracts/schemas/assess-map.schema.json": "<sha256>" }
}
```

- The consumer vendors `datapackage.json` and the verifier alongside the files it uses; a subset is fine, because the manifest pins every file and the verifier checks only the wanted ones.
- `commit` and `files` stay, so existing hash tests keep working unchanged, and a consumer that never adopts releases keeps working forever.
- The three PINS.json shapes in the family stay as they are; phase 3 adds the two fields to each. A shared pins schema is open question 8.

**Re-pin** (a session prepares it as a pull request in the consumer; the downloads and checks are read-only):

```bash
v=v1.1.0; old=v1.0.0; d=$(mktemp -d); mkdir "$d/new" "$d/old" "$d/pin"
gh release download "$v" -R avd-ops/avd-assess -p "avd-assess-${v#v}.zip" -D "$d/new"
gh release download "$v" -R avd-ops/avd-assess -p datapackage.json -D "$d/pin"   # the file whose hash goes in PINS.json
gh release download "$old" -R avd-ops/avd-assess -p "avd-assess-${old#v}.zip" -D "$d/old"
# 1. Provenance first, before anything from the download runs
gh attestation verify "$d/new/avd-assess-${v#v}.zip" -R avd-ops/avd-assess
gh attestation verify "$d/old/avd-assess-${old#v}.zip" -R avd-ops/avd-assess
gh attestation verify "$d/pin/datapackage.json" -R avd-ops/avd-assess
(cd "$d/new" && unzip -q "avd-assess-${v#v}.zip") && (cd "$d/old" && unzip -q "avd-assess-${old#v}.zip")
# 2. Hashes and schemas, with the verifier the consumer already vendors at its current pin
cmp "$d/pin/datapackage.json" "$d/new/datapackage.json"
python3 -I <consumer>/vendor/avd_assess_bundle.py "$d/new"
# 3. What changed between the two releases, with the diff from the old, attested release
python3 -I "$d/old/tools/diff_bundle.py" "$d/old" "$d/new"
```

`gh attestation verify` (GitHub CLI 2.49 or later) is the documented check because Cloud Shell's `gh` may be older than 2.81, which added `gh release verify` and `verify-asset`; where 2.81 is present, `gh release verify "$v"` also confirms the release is immutable. Both zips are attested before anything in them runs; the verifier that runs is the one already vendored, so a tampered bundle can't vouch for itself; an outsider with no earlier copy runs the in-bundle verifier only after the attestation check. `diff_bundle.py` compares two full releases, never a consumer's subset. Then copy the wanted files and `datapackage.json`, write `release`, `manifest`, `commit` and the file hashes, and run the consumer's tests. A re-pin is a reviewed pull request, never automatic. The weekly pins workflow in each consumer may report "avd-assess v1.2.0 is out (minor)" from `catalog.json`; it never moves a pin.

## 10. License and attribution

- Our files are MIT (`LICENSE`), and the manifest says so.
- A new `NOTICE` says what the data is made of: references link to and pin their sources (Microsoft Learn pages by `git_commit_id` and `updated_at`, GitHub sources by commit); a claim is one line in our own words; no table or text from a source is copied; the review checklist is cited by item short ID; Cloud Adoption Framework content (CC BY 4.0) is linked, never reproduced. A reader who reproduces a source must follow that source's license, not ours.
- Third-party products appear only as categories. `tests/check_wording.py` scans tracked files, so the release workflow runs it on the tag's checkout and runs the same pattern over the built bundle's files directly. Liquidware appears only in the notice and the partner rule.
- No tenant, customer, user or machine data is ever in the map; the release leak scan is the last gate.

## 11. How the other work fits

- **The endpoint map** (PR #39): `endpoints.json`, generated at the repo root by `build_index.py` with `"schema": "avd-assess-endpoints/v1"`, its schema `contracts/schemas/assess-endpoints.schema.json`, every row citing a `ref:` whose reference carries the Learn pin, never a copied endpoint table. It becomes one more resource. Its readers (avd-linecheck, the landing zone portal, avd-current-state, the shared portal engine) take it the same way: vendored at a release with the manifest, checked by the verifier or the browser equivalent. It changes on Microsoft's schedule, and an endpoint added is a minor bump, so readers that don't use it lose nothing by skipping a release.
- **The security review map** (PR #38): `security-review.json` becomes a resource when it merges; the avd-ops page vendors it at a release.
- **The shared portal engine** (avd-ops): its thread confirmed the shape fits. Portals run from Pages, any static host and `file://`, where `fetch()` and module imports are blocked, so a portal keeps another repo's data the way it does today: the JSON copy at a pin, inlined in the portal's own script, with a test that keeps the two equal (as the landing zone portal does with its platform list), and contract data through `contracts/PINS.json`. The engine never loads data; portals pass it in. The bundle stays plain JSON, one file per document, each with its schema; it is never a JavaScript module only. A browser check of a vendored file against the manifest uses `crypto.subtle.digest('SHA-256', ...)` and belongs to the engine.
- **The self-contained pair.** avd-landing-zone and avd-current-state keep vendored copies and read nothing at run time; the release adds a hash list and provenance on top of the commit pin they already use. Neither depends on Pages, the network, the brain or avd-swarm.

## 12. Migration for existing consumers

Nothing here changes a consumer until the owner says go, and each consumer moves at its next planned re-pin, one pull request each.

| Consumer | Pinned today | Moves to |
|---|---|---|
| avd-current-state `assess/PINS.json`, `contracts/PINS.json` | 7 files at `a5f4df1` | the first release, in the one re-pin planned after the last pillar PR; adds `release`, `manifest`, vendored `datapackage.json` and the PowerShell verifier; its Pester hash tests stay, one test calls `Get-AvdAssessBundleCheck` |
| avd-landing-zone `contracts/PINS.json` | 6 files at `b4209a7` (C14 from the brain stays separate) | the first release, adding the two fields to its `avd-assess` source entry |
| avd-second-brain `contracts/FOUNDATION-PINS.json` | 20 files at `ac7751d` | the first release; avd-swarm follows the brain as today |
| avd-ops security page | per PR #30 | the first release that carries `security-review.json` |
| avd-linecheck, portals, the portal engine | not yet | the first release that carries the endpoint map |

A consumer that stays on a commit pin keeps working; a release pin never invalidates one.

## 13. What this does not do

- No run-time fetch by any family tool, no auto-update, no automatic re-pin.
- No package registry, no container registry, no signing key.
- No Authenticode on the verifier. Vendored through git it carries no mark of the web, so `RemoteSigned` allows it. A Windows user who downloads the zip in a browser gets a blocked module under `RemoteSigned`; the documented path is `Unblock-File` after the attestation check, or the Python verifier. If an organization runs `AllSigned`, it re-signs, as decision 0008 expects.
- No change to how the map is authored: the YAML files and `build_index.py` stay as they are.

## 14. Build plan

| Phase | What | Who says go |
|---|---|---|
| 0 | This spec | the owner merges it |
| 1 | `scripts/bundle/build_bundle.py` (dry run in `check.yml`), `diff_bundle.py`, `tools/` verifiers with shared fixtures and tests in both languages, `contracts/schemas/assess-bundle.schema.json`, `NOTICE`, `$id` and the optional `deprecated` field on each schema (with a test that no schema uses a cross-file `$ref`, so no validator ever tries to resolve an `$id` over the network), the `.gitattributes` guard, `release.yml`, the `pages` job, the `v*` tag ruleset, the CLAUDE.md rule that sessions never tag | the owner, after the open questions |
| 2 | Immutable releases are already on for the organization (2026-10-21); the owner creates the `release` environment with the owner as required reviewer, enables Pages from Actions, and tags `v1.0.0` | the owner, in Cloud Shell |
| 3 | Consumers, one PR each, at their next re-pin (section 12), each with the brain and avd-swarm pair rule where it applies | the owner, per PR |

## 15. Red team

Fable reviewed the draft on 2026-10-21 and checked several facts directly (release downloads send no cross-origin header; `git archive` honors `core.autocrlf`; the gh versions). Every finding changed the spec:

| # | Severity | Finding | Change |
|---|---|---|---|
| 1 | high | A release published with the workflow token starts no `release: published` workflow, so Pages would never deploy | Pages is a job in `release.yml`, rerunnable by `workflow_dispatch` (section 5) |
| 2 | high | `git archive` applies `autocrlf`, `eol` and `export-*`, so bytes need not equal blobs | build from `git cat-file blob`, plus a `.gitattributes` guard (4.1) |
| 3 | high | The re-pin ran the verifier from inside the unverified bundle | attestation check of the zip first; run the consumer's already-vendored verifier (section 9) |
| 4 | high | Several bump rules weren't computable from two bundles | `idPaths` in the manifest, exact list of what's computed, `BREAKING:` declaration for meaning changes (section 6) |
| 5 | medium | Deprecation and removal rules contradicted each other | removal always major; the window is a gate on the major (section 6) |
| 6 | medium | A wall-clock `created` made the pinned manifest unreproducible | commit date, deterministic generator, twice-run test (4.2) |
| 7 | medium | Consumers don't mirror bundle paths; diff against a subset can't work | path map in both verifiers; diff two full releases (sections 8, 9) |
| 8 | medium | "Tag on main" in the tag's own workflow protects nothing | owner-only `v*` tag ruleset, actions pinned by SHA (section 7) |
| 9 | medium | A browser-downloaded `.psm1` is blocked by `RemoteSigned` | documented `Unblock-File` or Python path (section 13) |
| 10 | medium | Missing failure modes: draft left behind, Pages fails after publish, self-approval, old `gh` | "When a step fails" (section 7); `gh attestation verify` is the documented check (section 9) |
| 11 | low | Withdrawal lived only in mutable Pages | also in release notes (section 7) |
| 12 | low | GitHub's source archives aren't the bundle | said so (4.5) |
| 13 | low | The wording scan covers tracked files only; `schema_string` broke camelCase | scan the built bundle too (section 10); `schemaString` |
| 14 | low | A cross-file `$ref` would make validators fetch an `$id` | test that none exists (phase 1) |
| 15 | low | Missing questions | questions 11 to 13 |

A Claude code review of the PR then found ten more (a leftover `git archive` in section 7, the diff run from an unattested zip and a path that wasn't in the bundle, an `unzip` overwrite prompt, the build and diff order and the first release, the leak scan and the endpoint map's published Microsoft addresses, documents with no schema and a JSONL example, where deprecation marks are read, type and pattern changes a diff can't classify, and wildcards in `idPaths`); each is fixed in the section it names.

## 16. Open questions for the owner

1. **First release:** `v1.0.0`, cut after the endpoints and governance pillar (#34), the security review map (#38) and the endpoint map (#39) merge, so the planned single re-pin lands on it. **Answered (owner, 2026-10-21): yes.**
2. **Pages address:** **answered (owner, 2026-10-21): `assess.avd-ops.dev`**, a custom domain on this repo's own Pages. Phase 2 adds a DNS `CNAME` record `assess` pointing at `avd-ops.github.io` and verifies `avd-ops.dev` for the organization in GitHub, so no other account can claim the subdomain. Section 5 uses this address; every `$id` is under it.
3. **Immutable releases:** **answered and done (owner, 2026-10-21): turned on for the whole avd-ops organization.** No org repo had a tag, release or release workflow then, so nothing changed for existing work; every release from now on is locked once published.
4. **Release gate:** a `release` environment with you as required reviewer, so a tag alone publishes nothing? Recommended.
5. **Method and gap pages in the bundle** (zip only, about 1 MB in all)? Recommended yes, so the method travels with the data.
6. **Package registries** (PyPI, npm) later? Recommended no until an outside reader asks.
7. **SchemaStore listing** for editor completion? Recommended no until there is outside demand.
8. **One pins format:** make consumer `PINS.json` a shared contract (`avd-pins/v1`, numbered by you), or keep the three shapes and add two fields to each? Recommended: keep them, add the fields, revisit if a fourth shape appears.
9. **Cadence:** releases on demand (recommended), or a fixed rhythm such as monthly?
10. **Deprecation window:** an ID must be marked deprecated in a release at least 30 days before a major removes it. Right length?
11. **Cloud Shell's `gh` version:** if it is 2.81 or later, the re-pin block can add `gh release verify`; the spec assumes it may not be.
12. **Tags:** only you may create `v*` tags, by a ruleset? Recommended.
13. **Outside reproducibility of the leak scan:** ship `tests/public-ids.txt` in the bundle so anyone can rerun it? Recommended yes; it holds only Microsoft's published IDs.
