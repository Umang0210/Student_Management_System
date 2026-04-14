# Vercel Full Stack Deployment Guide

Your entire MERN app (frontend + backend) will be deployed on **Vercel**.

## Prerequisites
- GitHub repository with your code pushed
- MongoDB Atlas account (free tier available)
- Vercel account

---

## Step 1: Create MongoDB Atlas Cluster

### 1.1 Sign up / Log in to MongoDB Atlas
- Go to https://www.mongodb.com/cloud/atlas
- Create account or log in

### 1.2 Create a Free Cluster
1. Click "Create" → Choose "M0" (free tier)
2. Select your region (closest to you)
3. Click "Create Cluster" (takes ~5 minutes)

### 1.3 Create Database Access
1. Go to **Security** → **Database Access**
2. Click **Add New Database User**
3. Choose "Password" auth
4. Username: `admin`
5. Password: generate a strong password and save it
6. Click **Create User**

### 1.4 Configure Network Access
1. Go to **Security** → **Network Access**
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (required for serverless functions)
4. Click **Confirm**

### 1.5 Get Connection String
1. Go to **Databases** → Your cluster → Click **Connect**
2. Choose "Drivers"
3. Copy the connection string (looks like: `mongodb+srv://<username>:<password>@cluster.mongodb.net/`)
4. Replace `<username>` with your database user name
5. Replace `<password>` with your database user password
6. Replace `/` at the end with `/student_hub` (database name)
7. **Save this string securely** - you'll need it for Vercel (never commit to git)

---

## Step 2: Push Code to GitHub

```powershell
cd "c:/Users/umang/Desktop/mern project"
git add .
git commit -m "Setup Vercel full-stack deployment"
git push origin main
```

---

## Step 3: Deploy to Vercel

### 3.1 Connect GitHub to Vercel
1. Go to https://vercel.com
2. Click **Add New...** → **Project**
3. Select your GitHub repository
4. Click **Import**

### 3.2 Configure Environment Variables
Before deployment, add these environment variables:

| Key | Value |
|-----|-------|
| `MONGO_URL` | Your MongoDB Atlas connection string (from Step 1.5) |
| `DB_NAME` | `student_hub` |
| `ADMIN_EMAIL` | `admin@example.com` |
| `ADMIN_PASSWORD` | Your chosen admin password |
| `JWT_SECRET` | Generate a random string (e.g., `your-secret-key-12345`) |

**How to add:**
1. In Vercel project settings, go to **Environment Variables**
2. Add each variable one by one
3. Make sure they're available in **Production** and **Preview**

### 3.3 Deploy
1. Click **Deploy**
2. Wait for build to complete (~5-10 minutes)
3. Once done, you'll get a URL like: `https://your-project-name.vercel.app`

---

## Step 4: Update Frontend Environment Variables

Once Vercel deployment is complete and you have your project URL:

### 4.1 Update `.env.production`
Edit `frontend/.env.production`:
```
REACT_APP_BACKEND_URL=https://your-project-name.vercel.app/api
```

Replace `your-project-name` with your actual Vercel project name.

### 4.2 Push Changes
```powershell
git add frontend/.env.production
git commit -m "Update backend URL for production"
git push origin main
```

### 4.3 Redeploy Frontend
1. Go to Vercel project
2. Go to **Deployments**
3. Click **Redeploy** on your latest deployment
4. Vercel will rebuild with the new env var

---

## Step 5: Test Your Deployment

1. Visit: `https://your-project-name.vercel.app`
2. You should see the login page
3. Login with:
   - Email: `admin@example.com`
   - Password: Your `ADMIN_PASSWORD` from Step 3.2

4. After login, you should see the student dashboard
5. Try creating a student - should work with MongoDB Atlas

---

## Troubleshooting

### Blank Page After Login
- Check browser console (F12) for errors
- Verify `REACT_APP_BACKEND_URL` in `frontend/.env.production`
- Redeploy frontend after updating env var

### "Cannot connect to database"
- Verify MongoDB Atlas connection string in Vercel env vars
- Check that "Allow Access from Anywhere" is enabled in MongoDB Atlas
- Verify database name is `student_hub`

### Login Fails with 401
- Check that `ADMIN_EMAIL` and `ADMIN_PASSWORD` match in Vercel env vars
- Delete existing MongoDB Atlas data and redeploy to seed fresh admin user

### CORS Errors
- Frontend and backend URLs need to match in CORS configuration
- Restart Vercel deployment if you updated frontend URL

---

## URLs After Deployment

- **Frontend**: `https://your-project-name.vercel.app`
- **Backend API**: `https://your-project-name.vercel.app/api`
- **Login endpoint**: `https://your-project-name.vercel.app/api/auth/login`

---

## Next Steps

Your app is now fully deployed! To make updates:
1. Make changes locally
2. `git push origin main`
3. Vercel automatically redeploys

All environment variables are managed in Vercel → Project Settings → Environment Variables.
