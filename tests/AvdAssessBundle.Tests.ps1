# Personal project, not for production, as is; not affiliated with the author's employer, Liquidware or Microsoft.
#
# Runs tools/AvdAssessBundle.psm1 against the shared fixtures (tests/fixtures/bundle/cases.json), the
# same cases tests/check_bundle.py runs against the Python verifier. Pester 5, on Windows PowerShell 5.1
# and PowerShell 7. Set AVD_ASSESS_BUNDLE to a built bundle folder to check it too (CI does).

BeforeDiscovery {
    $fixtures = Join-Path $PSScriptRoot 'fixtures/bundle'
    # Hashtables, so Pester can name each test after the case.
    $script:Cases = @((Get-Content -Raw -LiteralPath (Join-Path $fixtures 'cases.json') | ConvertFrom-Json).cases | ForEach-Object {
            $h = @{}
            foreach ($p in $_.PSObject.Properties) { $h[$p.Name] = $p.Value }
            $h
        })
}

BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '../tools/AvdAssessBundle.psm1') -Force
    $script:Fixtures = Join-Path $PSScriptRoot 'fixtures/bundle'
    $script:CanValidate = $PSVersionTable.PSVersion -ge [version]'7.4'
}

Describe 'Get-AvdAssessBundleCheck on the shared fixtures' {
    It '<case>: <why>' -ForEach $Cases {
        $params = @{ Path = (Join-Path $Fixtures $_.case) }
        if ($_.ContainsKey('args')) {
            $a = $_.args
            if ($a.PSObject.Properties.Name -contains 'manifestSha256') { $params.ManifestSha256 = $a.manifestSha256 }
            if ($a.PSObject.Properties.Name -contains 'manifest') { $params.ManifestPath = $a.manifest }
            if ($a.PSObject.Properties.Name -contains 'pathMap') {
                $map = @{}
                foreach ($p in $a.pathMap.PSObject.Properties) { $map[$p.Name] = $p.Value }
                $params.PathMap = $map
            }
        }
        $results = @(Get-AvdAssessBundleCheck @params)
        $fails = @($results | Where-Object { $_.status -eq 'FAIL' })
        $fails.Count | Should -BeLessOrEqual 1
        if ($_.expect -eq 'PASS') {
            $fails.Count | Should -Be 0 -Because (($results | ForEach-Object { "$($_.id): $($_.detail)" }) -join '; ')
        }
        elseif ($_.expect -eq 'resource-schema' -and -not $CanValidate) {
            # Windows PowerShell 5.1 and PowerShell before 7.4 can't validate schemas: a WARN, never a PASS.
            ($results | Where-Object { $_.id -eq 'resource-schema' }).status | Should -Be 'WARN'
        }
        else {
            $fails[0].id | Should -Be $_.expect
        }
    }

    It 'emits the family check-item shape' {
        $item = Get-AvdAssessBundleCheck -Path (Join-Path $Fixtures 'good') | Select-Object -First 1
        @($item.PSObject.Properties.Name) | Should -Be @('id', 'status', 'detail')
    }

    It 'refuses a schema string the caller does not know' {
        $r = @(Get-AvdAssessBundleCheck -Path (Join-Path $Fixtures 'good') -KnownSchema 'avd-assess-map/v2')
        ($r | Where-Object { $_.status -eq 'FAIL' }).id | Should -Be 'resource-schema-string'
    }

    It 'warns, never passes, when it cannot validate schemas' -Skip:($PSVersionTable.PSVersion -ge [version]'7.4') {
        $r = @(Get-AvdAssessBundleCheck -Path (Join-Path $Fixtures 'good'))
        ($r | Where-Object { $_.id -eq 'resource-schema' }).status | Should -Be 'WARN'
    }
}

Describe 'Get-AvdAssessBundleCheck on a built bundle' -Skip:(-not $env:AVD_ASSESS_BUNDLE) {
    It 'passes the bundle scripts/bundle/build_bundle.py wrote' {
        $results = @(Get-AvdAssessBundleCheck -Path $env:AVD_ASSESS_BUNDLE)
        @($results | Where-Object { $_.status -eq 'FAIL' }).Count | Should -Be 0 -Because (($results | ForEach-Object { "$($_.id): $($_.detail)" }) -join '; ')
    }
}
