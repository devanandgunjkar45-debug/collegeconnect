# Render Deployment Guide for CampusConnect

## Prerequisites
1. GitHub account with your code pushed to a repository
2. Code must be on the `main` branch
3. Render.com account (free tier)

## Step-by-Step Deployment

### Step 1: Verify Configuration Files
All files have been updated:
- ✅ `render.yaml` - Updated with PostgreSQL and proper configuration
- ✅ `Dockerfile` - Updated with PostgreSQL dependencies
- ✅ `requirements.txt` - Added `dj-database-url` and `psycopg2-binary`
- ✅ `build.sh` - Created for migrations
- ✅ `campusconnect/settings.py` - Updated to use PostgreSQL

### Step 2: Push Changes to GitHub
```bash
git add .
git commit -m "Configure deployment for Render with PostgreSQL"
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

### Step 5: Update Environment Variables
1. In Render dashboard → Web Service → **"Environment"**
2. Add these environment variables:

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | Generate new: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://yourdomain.onrender.com` |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_USE_WHITENOISE` | `True` |
| `DB_ENGINE` | `postgresql` |

3. Click **"Save"** - service will redeploy

### Step 6: Run Initial Setup
After deployment completes:

1. In Render dashboard → Web Service → **"Shell"**
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
4. (Optional) Load sample data if you have fixtures

### Step 7: Verify Deployment
1. Visit `https://yourdomain.onrender.com`
2. Test login at `/admin`
3. Check that database is working

## Troubleshooting

### Deployment fails during collectstatic
- Ensure `STATIC_ROOT` and `STATICFILES_DIRS` are correct in settings.py
- Check that static files exist in the correct directories

### Database migration errors
- Check PostgreSQL service is created
- Verify `DATABASE_URL` environment variable is set
- Run migrations manually in Shell: `python manage.py migrate`

### 502 Bad Gateway
- Check application logs: **"Logs"** tab
- Ensure all required packages are in `requirements.txt`
- Verify gunicorn is running correctly

### Static files not loading
- Ensure `DJANGO_USE_WHITENOISE` is set to `True`
- Run collectstatic: `python manage.py collectstatic --noinput`

## Important Notes
- Free tier services sleep after 15 minutes of inactivity
- PostgreSQL free tier has 90-day data retention limit
- For production, consider upgrading to paid plans
- Keep backups of important data
- Update `yourdomain.onrender.com` with your actual Render URL everywhere it appears
