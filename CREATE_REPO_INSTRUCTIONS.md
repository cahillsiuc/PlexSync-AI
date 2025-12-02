# Create GitHub Repository - Instructions

## Option 1: Using GitHub Web Interface (Easiest)

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Or click the "+" icon in the top right → "New repository"

2. **Fill in the form:**
   - **Repository name:** `PlexSync-AI`
   - **Description:** `AI-Powered Invoice Synchronization System for Plex ERP`
   - **Visibility:** Choose Public or Private
   - ⚠️ **IMPORTANT:** Do NOT check:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   (We already have all of these!)

3. **Click "Create repository"**

4. **After creation, push your code:**
   ```bash
   git push -u origin main
   ```

---

## Option 2: Using PowerShell Script (Automated)

If you have a GitHub Personal Access Token:

1. **Get a GitHub Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a name: "PlexSync-AI"
   - Select scope: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Run the script:**
   ```powershell
   .\create_github_repo.ps1 -Token "YOUR_TOKEN_HERE"
   ```

3. **Or create private repository:**
   ```powershell
   .\create_github_repo.ps1 -Token "YOUR_TOKEN_HERE" -Private
   ```

---

## Option 3: Using GitHub API Directly

If you prefer using curl or have a token:

```powershell
$token = "YOUR_GITHUB_TOKEN"
$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}
$body = @{
    name = "PlexSync-AI"
    description = "AI-Powered Invoice Synchronization System for Plex ERP"
    private = $false
    auto_init = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

---

## After Repository is Created

Once the repository exists on GitHub, push your code:

```bash
git push -u origin main
```

If you get authentication errors:

### Using Personal Access Token:
```bash
# When prompted for password, use your token
git push -u origin main
```

### Using SSH (if you have SSH keys set up):
```bash
git remote set-url origin git@github.com:cahillsuc/PlexSync-AI.git
git push -u origin main
```

---

## Quick Checklist

- [ ] Repository created on GitHub
- [ ] Remote is set: `git remote -v` shows your repo
- [ ] Code is committed: `git log` shows your commit
- [ ] Push command ready: `git push -u origin main`

---

**Recommended:** Use Option 1 (Web Interface) - it's the simplest and most reliable!

