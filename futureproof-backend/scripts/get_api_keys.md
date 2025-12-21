# 🔑 API Keys Collection Guide

Follow these steps to get all required API keys for FutureProof.

## 1. Groq API Key (FREE) ✅

**Why**: Powers AI agents for code analysis

**Steps**:
1. Go to: https://console.groq.com/
2. Sign up with Google/GitHub
3. Click "API Keys" in sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)
6. Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

**Cost**: FREE (no credit card required)

---

## 2. GitHub Personal Access Token ✅

**Why**: Clone repositories and create PRs

**Steps**:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `FutureProof Hackathon`
4. Select scopes:
   - ✅ `repo` (all)
   - ✅ `workflow`
5. Click "Generate token"
6. Copy the token (starts with `ghp_...`)
7. Add to `.env`: `GITHUB_TOKEN=ghp_your_token_here`

**Cost**: FREE

---

## 3. CodeRabbit API Key

**Why**: Code review and PR comments

**Steps**:
1. Go to: https://coderabbit.ai/
2. Sign up with GitHub
3. Go to Settings → API Keys
4. Generate new API key
5. Copy the key
6. Add to `.env`: `CODERABBIT_API_KEY=your_key_here`

**Cost**: Check if they offer hackathon credits (likely free tier available)

**Alternative**: If not available, comment out CodeRabbit code - not critical for demo

---

## 4. Cline (Optional)

**Why**: Autonomous coding environment

**Steps**:
1. Cline CLI is installed via npm (already in Dockerfile)
2. Check: https://cline.bot/ for API key if required
3. If no API key needed, leave blank in `.env`

**Cost**: Likely FREE for CLI usage

---

## 5. Hugging Face Token (Optional for Oumi)

**Why**: Download models for Oumi fine-tuning

**Steps**:
1. Go to: https://huggingface.co/settings/tokens
2. Create new token with `read` access
3. Copy token
4. Add to `.env`: `HUGGINGFACE_TOKEN=hf_your_token_here`

**Cost**: FREE

---

## 6. Kestra (No API Key Needed) ✅

**Why**: Workflow orchestration

**Setup**: Runs locally via Docker (no API key required)

---

## Required vs Optional Keys

### ✅ REQUIRED (Get these first):
- `GROQ_API_KEY` - Core AI functionality
- `GITHUB_TOKEN` - Repository access
- `SECRET_KEY` - Generate random string: `openssl rand -hex 32`

### 📦 RECOMMENDED:
- `CODERABBIT_API_KEY` - Improves demo quality

### 🎁 OPTIONAL (Nice to have):
- `HUGGINGFACE_TOKEN` - For Oumi model downloads
- `CLINE_API_KEY` - If required by Cline

---

## Quick Start Configuration

**Minimum viable .env**:
