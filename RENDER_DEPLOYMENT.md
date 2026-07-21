# Render Deployment Guide for CampusConnect

## Prerequisites
1. GitHub account with your code pushed to a repository
2. Code must be on the `main` branch
3. Render.com account (free tier)

## Step-by-Step Deployment

### Step 1: Verify Configuration Files
All files have been updated:
- ✅ `render.yaml` - Updated with PostgreSQL and proper configuration
- ✅ `Dockerfile` - Updated with PostgreSQL dependencies and startup script
- ✅ `start.sh` - Created for running migrations and starting app
- ✅ `requirements.txt` - Added `dj-database-url` and `psycopg2-binary`
- ✅ `campusconnect/settings.py` - Updated to use PostgreSQL

### Step 2: Push Changes to GitHub
```bash
git add .
git commit -m "Configure deployment for Render with PostgreSQL and startup script"
git push origin main
```

### Step 3: Deploy on Render
1. Go to [https://render.com](https://render.com)
2. Sign in or create account
3. Click **"New +"** → **"Blueprint"**
4. Select **"Public Git Repository"**
5. Paste your GitHub repository URL
6. Click **"Connect"**
7. Render will detect `render.yaml` and show the configuration
8. Review and click **"Create New Services"**
9. Wait 10-15 minutes for deployment to complete

### Step 4: Get Your Service URL
- After deployment, go to your web service dashboard
- Copy your service URL (looks like: `yourapp.onrender.com`)
- The migrations will run automatically on first deployment via `start.sh`

### Step 5: Update Environment Variables
1. In Render dashboard → Web Service → **"Environment"**
2. Add/Update these environment variables:

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | Generate new: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://yourdomain.onrender.com` |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_USE_WHITENOISE` | `True` |
| `DB_ENGINE` | `postgresql` |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` |

3. Click **"Save"** - service will redeploy automatically

### Step 6: Verify Deployment
1. Visit `https://yourdomain.onrender.com`
2. Test login at `/admin`
3. Check that database is working
4. Monitor logs for any errors

### Step 7: (Optional) Create Superuser Manually
If migrations ran but you need to create a superuser:

1. In Render dashboard → Web Service → **"Shell"**
2. Run:
   ```bash
   python manage.py createsuperuser
   ```

## What Happens Automatically

When the app starts on Render:
1. `start.sh` runs automatically
2. Database migrations are applied
3. Static files are collected
4. Gunicorn server starts

## Troubleshooting

### Deployment fails during build
- Check Render logs: **"Logs"** tab
- Ensure all requirements are in `requirements.txt`
- Verify `start.sh` has correct permissions

### Database migration errors
- Check PostgreSQL service is created in render.yaml
- Verify `DATABASE_URL` environment variable is set
- View logs to see specific error messages
- Manual migration: Go to Shell and run `python manage.py migrate`

### 502 Bad Gateway
- Check application logs in Render dashboard
- Ensure `DJANGO_ALLOWED_HOSTS` includes your Render domain
- Verify all environment variables are set correctly
- Check that SECRET_KEY is set and not empty

### Static files not loading
- Ensure `DJANGO_USE_WHITENOISE` is set to `True`
- Check that `STATIC_ROOT` and `STATICFILES_DIRS` are correct
- Verify static files exist in your repository
- Clear browser cache and hard refresh (Ctrl+Shift+R)

### Can't login to admin panel
- Verify migrations ran successfully (check logs)
- Create superuser via Shell tab if needed
- Check `DJANGO_DEBUG` is `False` for production
- Verify `DJANGO_ALLOWED_HOSTS` is correct

## Important Notes
- Free tier services sleep after 15 minutes of inactivity
- PostgreSQL free tier has 90-day data retention limit
- For production, consider upgrading to paid plans
- Keep backups of important data
- Update `yourdomain.onrender.com` with your actual Render URL everywhere it appears
- Never commit `.env` file with sensitive keys to GitHub
- Use environment variables for all sensitive configuration

