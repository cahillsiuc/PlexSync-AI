# Interactive script to create GitHub repository
# Securely prompts for GitHub Personal Access Token

Write-Host "`n=== Create GitHub Repository ===`n" -ForegroundColor Cyan

$repoName = "PlexSync-AI"
$description = "AI-Powered Invoice Synchronization System for Plex ERP"

Write-Host "Repository Details:" -ForegroundColor Yellow
Write-Host "  Name: $repoName" -ForegroundColor White
Write-Host "  Description: $description" -ForegroundColor White
Write-Host ""

# Prompt for token
Write-Host "To create the repository, you need a GitHub Personal Access Token." -ForegroundColor Yellow
Write-Host ""
Write-Host "If you don't have one:" -ForegroundColor Cyan
Write-Host "  1. Visit: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "  2. Click 'Generate new token (classic)'" -ForegroundColor White
Write-Host "  3. Select 'repo' scope" -ForegroundColor White
Write-Host "  4. Generate and copy the token" -ForegroundColor White
Write-Host ""

$token = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
$tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
)

if ([string]::IsNullOrWhiteSpace($tokenPlain)) {
    Write-Host "`n❌ Token is required. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "`nCreating repository..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "token $tokenPlain"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = $repoName
    description = $description
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    
    Write-Host "`n✅ Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
    Write-Host "Clone URL: $($response.clone_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Now pushing your code..." -ForegroundColor Yellow
    
    # Clear the token from memory
    $tokenPlain = $null
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
    
    return $response
} catch {
    Write-Host "`n❌ Error creating repository:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host ""
        Write-Host "Authentication failed. Please check your token." -ForegroundColor Yellow
        Write-Host "Make sure the token has 'repo' scope." -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host ""
        Write-Host "Repository might already exist. Trying to push anyway..." -ForegroundColor Yellow
        Write-Host "Run: git push -u origin main" -ForegroundColor Cyan
    }
    
    exit 1
}

