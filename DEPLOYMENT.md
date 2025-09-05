# Chess AI Bot - GitHub Pages Deployment

This guide explains how to deploy your Chess AI Bot to GitHub Pages.

## Prerequisites

1. A GitHub repository with your code
2. Your backend deployed on Render (or another hosting service)
3. GitHub Pages enabled on your repository

## Deployment Steps

### 1. Update Repository Settings

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Scroll down to "Pages" section
4. Under "Source", select "GitHub Actions"

### 2. Update Homepage URL

In `frontend/chess-web/package.json`, replace `yourusername` with your actual GitHub username:

```json
"homepage": "https://yourusername.github.io/chess-ai-bot"
```

### 3. Deploy Backend (if not already done)

Your backend is already configured for Render deployment via `render.yaml`. Make sure it's deployed and running.

### 4. Push to Main Branch

The GitHub Actions workflow will automatically:
- Build your React frontend
- Deploy it to GitHub Pages
- Use your Render backend URL

```bash
git add .
git commit -m "Add GitHub Pages deployment"
git push origin main
```

### 5. Access Your App

After deployment, your chess app will be available at:
`https://yourusername.github.io/chess-ai-bot`

## How It Works

- **Frontend**: Deployed to GitHub Pages (static hosting)
- **Backend**: Deployed to Render (server hosting)
- **Communication**: Frontend makes API calls to Render backend

## Troubleshooting

1. **Build fails**: Check that all dependencies are in `package.json`
2. **Backend not responding**: Verify your Render deployment is running
3. **CORS errors**: Ensure your backend has CORS enabled (already configured)
4. **404 on GitHub Pages**: Check that the homepage URL in `package.json` matches your repository

## Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
cd frontend/chess-web
npm install
REACT_APP_BACKEND_URL=https://your-backend-url.onrender.com npm run build
# Then upload the 'build' folder contents to GitHub Pages
```