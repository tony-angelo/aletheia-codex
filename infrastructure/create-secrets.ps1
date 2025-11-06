# AletheiaCodex Secret Manager Setup Script (create-or-update)

$PROJECT_ID = "aletheia-codex-prod"

Write-Host "Creating/updating secrets for: $PROJECT_ID" -ForegroundColor Green

function Test-SecretExists {
  param([string]$name)
  $null = gcloud secrets describe $name --project=$PROJECT_ID 2>$null
  if ($LASTEXITCODE -eq 0) { return $true } else { return $false }
}

function Upsert-Secret {
  param([string]$name, [string]$value)

  if ([string]::IsNullOrWhiteSpace($value)) {
    throw "Value for secret '$name' is empty. Aborting."
  }

  if (Test-SecretExists -name $name) {
    Write-Host "Adding new version to existing secret: $name" -ForegroundColor Yellow
    $value | gcloud secrets versions add $name `
      --data-file=- `
      --project=$PROJECT_ID | Out-Null
  } else {
    Write-Host "Creating secret: $name" -ForegroundColor Green
    $value | gcloud secrets create $name `
      --data-file=- `
      --replication-policy="automatic" `
      --project=$PROJECT_ID | Out-Null
  }
}

# Read Neo4j credentials from file
$neoPath = ".\infrastructure\neo4j-credentials.txt"
if (-not (Test-Path $neoPath)) { throw "File not found: $neoPath" }
$neoRaw = Get-Content -Raw $neoPath

$NEO4J_URI      = ([regex]::Match($neoRaw, 'URI:\s*(.+)')).Groups[1].Value.Trim()
$NEO4J_USER     = ([regex]::Match($neoRaw, 'Username:\s*(.+)')).Groups[1].Value.Trim()
$NEO4J_PASSWORD = ([regex]::Match($neoRaw, 'Password:\s*(.+)')).Groups[1].Value.Trim()

# Read Gemini API key from file
$gemPath = ".\infrastructure\gemini-api-key.txt"
if (-not (Test-Path $gemPath)) { throw "File not found: $gemPath" }
$gemRaw = Get-Content -Raw $gemPath
$GEMINI_API_KEY = ([regex]::Match($gemRaw, 'API_KEY:\s*(.+)')).Groups[1].Value.Trim()

# Preview (mask sensitive)
Write-Host "NEO4J_URI: $NEO4J_URI"
Write-Host "NEO4J_USER: $NEO4J_USER"
Write-Host "NEO4J_PASSWORD: " ("*" * 8)
Write-Host "GEMINI_API_KEY: " ("*" * 8)

# Upsert secrets
Upsert-Secret -name "NEO4J_URI"      -value $NEO4J_URI
Upsert-Secret -name "NEO4J_USER"     -value $NEO4J_USER
Upsert-Secret -name "NEO4J_PASSWORD" -value $NEO4J_PASSWORD
Upsert-Secret -name "GEMINI_API_KEY" -value $GEMINI_API_KEY

Write-Host "Secrets upsert complete." -ForegroundColor Green
