# PowerShell script to create GitHub repository
# Requires GitHub Personal Access Token with 'repo' scope

param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [Parameter(Mandatory=$false)]
    [string]$Name = "PlexSync-AI",
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "AI-Powered Invoice Synchronization System for Plex ERP",
    
    [Parameter(Mandatory=$false)]
    [switch]$Private
)

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = $Name
    description = $Description
    private = $Private.IsPresent
    auto_init = $false
    gitignore_template = ""
    license_template = ""
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    
    Write-Host "✅ Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Now you can push your code:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor White
    
    return $response
} catch {
    Write-Host "❌ Error creating repository:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host ""
        Write-Host "Authentication failed. Please check your token." -ForegroundColor Yellow
        Write-Host "Get a token at: https://github.com/settings/tokens" -ForegroundColor Cyan
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host ""
        Write-Host "Repository might already exist or name is invalid." -ForegroundColor Yellow
    }
    
    exit 1
}

