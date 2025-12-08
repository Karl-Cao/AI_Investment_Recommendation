# ✅ Deployment Checklist

## Pre-Deployment Security Check

Before pushing to GitHub, verify these items:

- [x] API key is in `.streamlit/secrets.toml` (not in code)
- [x] `.gitignore` includes `.streamlit/secrets.toml`
- [x] No hardcoded credentials in any Python files
- [x] `secrets.toml.example` template is created
- [x] All dependencies listed in `requirements.txt`

## Verification Commands

Run these to confirm everything is secure:

```bash
# 1. Verify secrets.toml is ignored
git check-ignore -v .streamlit/secrets.toml
# Expected: .gitignore:5:secrets.toml	.streamlit/secrets.toml

# 2. Check what will be committed
git status

# 3. Search for API keys in tracked files (should return nothing)
git grep -i "sk-ant"

# 4. Verify secrets.toml is not staged
git status | grep "secrets.toml"
# Should only show: .streamlit/secrets.toml.example
```

## Files Ready for GitHub

### ✅ New Files to Push:
- `README.md` - Main project documentation
- `README_BACKTEST.md` - Backtest feature details
- `GITHUB_SETUP.md` - GitHub deployment guide
- `DEPLOYMENT_CHECKLIST.md` - This file
- `backtest_performance.py` - Backtesting implementation
- `test_yfinance.py` - API testing utility
- `.streamlit/secrets.toml.example` - API key template
- `push_to_github.bat` - Quick push script

### 📝 Modified Files:
- `app.py` - Added streaming chat & backtest UI
- `.gitignore` - Enhanced security rules
- `requirements.txt` - Updated dependencies

### 🚫 Ignored Files (Won't be pushed):
- `.streamlit/secrets.toml` - YOUR API KEY (kept secret!)
- `__pycache__/` - Python cache
- `.vscode/`, `.idea/` - IDE configs

## Quick Push to GitHub

### Option 1: Use the Batch Script (Windows)
```bash
# Run the automated script
push_to_github.bat
```

### Option 2: Manual Commands
```bash
# 1. Stage all changes
git add .

# 2. Verify (make sure secrets.toml is NOT listed)
git status

# 3. Commit
git commit -m "Add streaming chat, backtest feature, and comprehensive documentation"

# 4. Push
git push origin main
```

## Deploy to Streamlit Cloud

After pushing to GitHub:

1. **Go to**: https://share.streamlit.io

2. **Create New App**
   - Repository: `AI_Investment_Recommendation`
   - Branch: `main`
   - Main file: `app.py`

3. **Add Secrets** (Click "Advanced settings" before deploying)
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
   ```

4. **Click "Deploy"** and wait 2-3 minutes

5. **Share the URL** - Your app is now live! 🎉

## Post-Deployment Verification

After deploying:

1. **Check GitHub**
   - Visit your repo: `https://github.com/YOUR_USERNAME/AI_Investment_Recommendation`
   - Search for "sk-ant" (should find NOTHING)
   - Verify `.streamlit/secrets.toml` is NOT visible
   - Confirm README displays properly

2. **Test Streamlit App**
   - Open your Streamlit Cloud URL
   - Test the chat (verify API key works)
   - Check all tabs load
   - Run a backtest

3. **Security Final Check**
   - View page source (Ctrl+U) - should NOT contain API key
   - Check browser console - no API key errors
   - Verify secrets are loaded from Streamlit Cloud

## Troubleshooting

### Problem: API key error on Streamlit Cloud
**Solution**:
- Go to Streamlit Cloud dashboard
- Click on your app → Settings → Secrets
- Paste your API key in TOML format
- Reboot the app

### Problem: "Module not found" error
**Solution**:
- Check `requirements.txt` has all dependencies
- Git push the updated requirements.txt
- Streamlit Cloud will auto-redeploy

### Problem: Accidentally committed secrets
**Solution**:
1. **Immediately** rotate your API key at https://console.anthropic.com/
2. Delete the exposed key
3. Create a new one
4. Update local `secrets.toml`
5. Contact GitHub support to purge history (if public repo)

## Success Indicators

You'll know everything worked when:

- ✅ GitHub repo shows all your files (except secrets)
- ✅ Streamlit app loads without errors
- ✅ Chat responds with AI messages
- ✅ Backtest analysis runs successfully
- ✅ No API key visible in public code
- ✅ README renders nicely on GitHub

## Next Steps

After successful deployment:

1. **Add a nice README badge** showing app status
2. **Share your app URL** on social media
3. **Consider adding**:
   - GitHub Actions for CI/CD
   - Unit tests
   - More backtesting features
4. **Monitor usage** on Anthropic dashboard

---

**Ready to deploy? Follow this checklist and you're good to go!** 🚀

Last updated: December 2025
