# Before Publishing to GitHub - Customization Checklist

This file contains instructions for personalizing the project before publishing to your public GitHub repository. Delete this file after completing the checklist.

## ✅ Required Customizations

### 1. Update GitHub Username
Search and replace `najeebpk-dev` with your actual GitHub username in:
- [ ] README.md (2 occurrences)
- [ ] setup.py (1 occurrence)
- [ ] pyproject.toml (4 occurrences)
- [ ] CONTRIBUTING.md (1 occurrence)
- [ ] SECURITY.md (1 occurrence)
- [ ] docs/DEPLOYMENT.md (1 occurrence)

**Quick PowerShell command:**
```powershell
# Replace 'YOUR_GITHUB_USERNAME' with your actual username
$username = "YOUR_GITHUB_USERNAME"
Get-ChildItem -Recurse -File -Include *.md,*.py,*.toml | 
    ForEach-Object {
        (Get-Content $_.FullName) -replace 'najeebpk-dev', $username | 
        Set-Content $_.FullName
    }
```

### 2. Add Your Contact Information

**README.md** (near end of file):
- [ ] Add your LinkedIn profile URL
- [ ] Optionally add your email or preferred contact method

**setup.py** (line 14-15):
- [ ] Update author name if desired (currently: "Enterprise AI Search Contributors")
- [ ] Update email if desired (currently: "contact@example.com")

**pyproject.toml** (line 13):
- [ ] Update author name if desired
- [ ] Update email if desired

### 3. Verify .gitignore is Working

Ensure these files are NOT committed:
- [ ] .env (should be ignored)
- [ ] .venv/ (should be ignored)
- [ ] __pycache__/ (should be ignored)
- [ ] data/documents/*.pdf (should be ignored)

**Check with:**
```powershell
git status --ignored
```

### 4. Optional Customizations

**Project Name** - If you want to rename the project:
- [ ] Update in README.md title
- [ ] Update in setup.py
- [ ] Update in pyproject.toml
- [ ] Rename the GitHub repository

**License** - Current: MIT License
- [ ] Review LICENSE file
- [ ] Update copyright holder if needed (currently: "Enterprise AI Search Contributors")

**Badges in README.md** - Update or add:
- [ ] Add your actual build status badge (after setting up GitHub Actions)
- [ ] Add code coverage badge (after running tests)
- [ ] Consider adding: License badge, Python version badge, etc.

### 5. Pre-Publication Checklist

**Code Quality:**
- [ ] Run: `python setup_check.py` (should pass all checks)
- [ ] Run: `pytest tests/` (if you've added tests)
- [ ] Run: `black src/` (format code)
- [ ] Run: `flake8 src/` (check linting)

**Documentation:**
- [ ] Review README.md for accuracy
- [ ] Check all links work (GitHub won't exist until published)
- [ ] Add screenshots or demo GIF if desired

**Security:**
- [ ] Confirm .env is in .gitignore
- [ ] Confirm no API keys in code
- [ ] Review SECURITY.md

**Git Setup:**
- [ ] Initialize git if not already done: `git init`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Initial commit"`
- [ ] Create GitHub repo
- [ ] Add remote: `git remote add origin https://github.com/najeebpk-dev/enterprise-ai-search.git`
- [ ] Push: `git push -u origin main`

### 6. After Publishing

- [ ] Enable GitHub Actions (CI will run automatically)
- [ ] Add repository description and topics on GitHub
- [ ] Create first release/tag (v1.0.0)
- [ ] Update any absolute paths if needed
- [ ] Star your own repo (optional but why not! 😊)
- [ ] Share on LinkedIn/Twitter/etc.

### 7. Optional Enhancements

**README Badges to Add:**
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
```

**GitHub Repository Settings:**
- Enable: Issues, Discussions (optional), Security alerts
- Add Topics: `azure`, `openai`, `rag`, `search`, `nlp`, `python`, `ai`
- Add repository description: "Enterprise-grade document search with RAG capabilities using Azure Cognitive Search and Azure OpenAI"

**Portfolio Enhancement:**
- Add screenshots of the CLI interface
- Create a demo video or GIF
- Add a "How it Works" section with architecture diagrams
- Link to live demo (if deployed)

## 📝 Quick Start Commands

```powershell
# 1. Customize username (replace YOUR_USERNAME)
$username = "YOUR_USERNAME"
Get-ChildItem -Recurse -File -Include *.md,*.py,*.toml | ForEach-Object {
    (Get-Content $_.FullName) -replace 'najeebpk-dev', $username | Set-Content $_.FullName
}

# 2. Verify no sensitive files will be committed
git status --ignored

# 3. Run quality checks
python setup_check.py
black src/
flake8 src/

# 4. Initialize and publish
git init
git add .
git commit -m "Initial commit: Enterprise AI Search with RAG"
# Create repo on GitHub, then:
git remote add origin https://github.com/$username/enterprise-ai-search.git
git branch -M main
git push -u origin main
```

## ⚠️ Important Notes

1. **Never commit .env file** - It's in .gitignore but double-check
2. **API keys** - Use GitHub Secrets for CI/CD, not hardcoded values
3. **Personal info** - Review all files for any personal information
4. **Test locally first** - Run `python setup_check.py` before publishing

## 🎉 When Complete

Delete this file (`BEFORE_PUBLISHING.md`) before final commit, or add it to .gitignore!

---

**Remember:** This is YOUR portfolio project. Feel free to customize, extend, and make it unique!
