# 📤 GitHub Setup Guide

This guide will help you push your AI Investment Recommendation project to GitHub safely.

## ✅ Pre-Push Checklist

Before pushing to GitHub, verify:

1. **✓ Secrets are protected**
   ```bash
   git check-ignore -v .streamlit/secrets.toml
   ```
   Should show: `.gitignore:5:secrets.toml	.streamlit/secrets.toml`

2. **✓ No API keys in code**
   - All API keys are in `.streamlit/secrets.toml`
   - No hardcoded credentials in any `.py` files

3. **✓ .gitignore is updated**
   - Contains `.streamlit/secrets.toml`
   - Contains `*.env` and other sensitive files

## 🚀 Push to GitHub

### Option 1: First Time Setup (New Repository)

1. **Create a new repository on GitHub**
   - Go to https://github.com/new
   - Name: `AI_Investment_Recommendation`
   - Description: "AI-powered investment analysis with Claude"
   - **Keep it Public or Private** (your choice)
   - **Do NOT initialize with README** (we already have one)

2. **Add and commit your changes**
   ```bash
   cd "c:\Users\Karl1\Desktop\AI_Investment_Recommendation"

   # Add all new files
   git add .

   # Check what will be committed (make sure secrets.toml is NOT listed)
   git status

   # Commit with a descriptive message
   git commit -m "Add streaming chat, backtest feature, and comprehensive documentation"
   ```

3. **Connect to GitHub and push**
   ```bash
   # Replace YOUR_USERNAME with your GitHub username
   git remote add origin https://github.com/YOUR_USERNAME/AI_Investment_Recommendation.git

   # Push to GitHub
   git push -u origin main
   ```

### Option 2: Update Existing Repository

If you already have a GitHub repository:

1. **Pull latest changes first**
   ```bash
   cd "c:\Users\Karl1\Desktop\AI_Investment_Recommendation"
   git pull origin main
   ```

2. **Add and commit your changes**
   ```bash
   # Add all modified and new files
   git add .

   # Verify secrets.toml is NOT in the list
   git status

   # Commit
   git commit -m "Add streaming chat, backtest feature, and comprehensive documentation

   - Implemented streaming responses for chat interface
   - Added portfolio backtesting feature with NASDAQ comparison
   - Created comprehensive README and documentation
   - Updated dependencies and gitignore
   - Added test utilities for yfinance API"
   ```

3. **Push to GitHub**
   ```bash
   git push origin main
   ```

## 🔒 Security Verification

After pushing, verify security:

1. **Check GitHub repository**
   - Go to your repository on GitHub
   - Search for "sk-ant" (API key prefix) - should find NOTHING
   - Check that `.streamlit/secrets.toml` is NOT in the file list
   - Verify `.streamlit/secrets.toml.example` IS there (template only)

2. **If you accidentally committed secrets:**
   ```bash
   # DO NOT just delete and recommit - it's still in history!
   # Instead, rotate your API key immediately:
   # 1. Go to https://console.anthropic.com/
   # 2. Delete the exposed API key
   # 3. Create a new one
   # 4. Update your local secrets.toml
   # 5. Then clean git history (advanced, see GitHub docs)
   ```

## 📋 What Gets Pushed vs Ignored

### ✅ Files that WILL be pushed:
- `app.py` (main application)
- `backtest_performance.py` (backtesting logic)
- `test_yfinance.py` (API testing)
- `README.md` (project documentation)
- `README_BACKTEST.md` (backtest docs)
- `requirements.txt` (dependencies)
- `.gitignore` (ignore rules)
- `.streamlit/secrets.toml.example` (template)
- `data/` folder (company data)

### ❌ Files that will NOT be pushed (protected):
- `.streamlit/secrets.toml` (contains API key!)
- `__pycache__/` (Python cache)
- `.vscode/`, `.idea/` (IDE settings)
- `*.pyc` (compiled Python)
- `.env` files

## 🌐 Deploy to Streamlit Cloud

After pushing to GitHub:

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub

2. **Deploy your app**
   - Click "New app"
   - Select your repository: `AI_Investment_Recommendation`
   - Main file: `app.py`
   - Click "Advanced settings"

3. **Add secrets**
   - In "Secrets" section, paste:
   ```toml
   ANTHROPIC_API_KEY = "your-actual-api-key-here"
   ```
   - Click "Deploy"

4. **Your app is live!**
   - Share the URL with others
   - They won't see your API key (it's secure on Streamlit Cloud)

## 🛠️ Common Commands

```bash
# Check what will be committed
git status

# See differences
git diff

# Add specific files only
git add app.py backtest_performance.py

# Unstage a file
git restore --staged filename.py

# View commit history
git log --oneline

# Create a new branch for features
git checkout -b feature/new-feature

# Switch back to main
git checkout main

# See remote repository URL
git remote -v
```

## ⚠️ Important Reminders

1. **Never commit secrets.toml** - It's in .gitignore, but double-check before pushing
2. **Always check `git status`** before committing
3. **Use meaningful commit messages** - Explain what changed and why
4. **Pull before push** - Avoid conflicts with remote changes
5. **Rotate API keys if exposed** - Better safe than sorry

## 📞 Need Help?

- Git documentation: https://git-scm.com/doc
- GitHub guides: https://guides.github.com/
- Streamlit deployment: https://docs.streamlit.io/streamlit-community-cloud

---

**Ready to push? Follow the steps above and your code will be safely on GitHub!** 🚀
