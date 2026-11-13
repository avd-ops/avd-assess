# Case study: Migrating standing Bicep stacks to Terraform without recreation

*Personal project, not for production use. Provided as is, without warranty of any kind. Not affiliated with the author's employer, Liquidware, or Microsoft.*

## Scenario

An Azure Virtual Desktop (AVD) environment with standing shared services — a shared Azure Compute Gallery with image-builder managed identities, plus an Automation Account and Storage Account for run history and cost-guardrail schedules — transitions its Infrastructure as Code (IaC) standard from Bicep to Terraform (HCL).

Bicep is stateless: removing or refactoring a resource in `.bicep` leaves it orphaned in Azure unless wrapped in Deployment Stacks, and moving to Terraform via destroy-and-recreate risks:
- Breaking RBAC assignments when managed identity principal IDs change.
- Deleting durable audit logs, run records, or published Compute Gallery image versions.

## Method

1. **Classify standing stacks:**
   - *Ephemeral / replaceable* (dev/test VMs) -> rewrite in HCL and retire Bicep templates.
   - *Stateful / identity-bound* (run-history storage, automation schedules, image gallery) -> adopt in-place via Terraform `import` blocks.
2. **Pre-migration safety gates:**
   - Capture a fresh read-only estate snapshot (`avd-current-state`) as the baseline.
   - Confirm no active Automation schedules or running jobs exist.
   - Export and SHA-256 verify all durable storage blobs before touching Terraform state.
3. **Import & zero-destroy / zero-replace gate:**
   - Map each live ARM resource ID to its HCL `import {}` block.
   - Require `terraform plan` to show **0 to destroy** and **0 to replace** before running `terraform apply`. Fix HCL attributes to match live ARM properties if any replacement is planned.
   - Remove temporary `import {}` blocks after `apply` and confirm a clean `terraform plan` (`No changes`).
   - Rollback is state-only (`terraform state rm`); never run `terraform destroy` on imported standing resources.
4. **Post-migration verification:**
   - Verify live blob counts and hashes match the pre-migration manifest.
   - Re-run the read-only estate collector and health checks against the baseline.

## Results & lessons from live execution

- **Standing image gallery stack:** Adopted 7 resources (resource group, Compute Gallery, Gen2 Trusted Launch image definition, 2 user-assigned managed identities, 2 RBAC role assignments) with `7 imported, 0 added, 0 changed, 0 destroyed` and a clean post-import `plan`.
- **Standing recorder & deadline automation stack:** Backed up 450 blobs with a SHA-256 manifest, then adopted 10 resources (resource group, keyless storage account, 2 containers, Automation Account, PowerShell deadline runbook, subscription diagnostic setting, 3 RBAC role assignments) with `10 imported, 0 added, 0 changed, 0 destroyed` and a clean post-import `plan`.

### Key provider & parity lessons

1. **Keyless storage accounts require `storage_use_azuread = true` on `provider "azurerm"`:** Importing a storage account with `shared_access_key_enabled = false` fails data-plane reads (`403 KeyBasedAuthenticationNotPermitted`) unless `storage_use_azuread = true` is configured on the provider.
2. **ARM resource ID casing in role assignment `scope`:** Azure's role assignment API can return `/resourcegroups/` (lowercase) while Terraform's `azurerm_storage_container.*.id` emits `/resourceGroups/` (camelCase), triggering a `ForceNew` replacement (`-/+`) on import. Normalizing the segment casing in HCL (`replace(..., "resourceGroups", "resourcegroups")`) — noting that Terraform's `replace()` treats `/.../` as regex — keeps the import at 0 replace.
3. **Automation runbook line-ending normalization:** `azurerm_automation_runbook` compares `content` byte-for-byte; CRLF/LF differences between checkouts and ARM cause spurious full-file diffs. Use `lifecycle { ignore_changes = [content] }` during adoption or normalize line endings explicitly.
4. **Separate standing-adoption roots from greenfield modules:** Adopting existing Bicep-named resources into dedicated adoption roots avoids forcing replacement against greenfield naming conventions.
