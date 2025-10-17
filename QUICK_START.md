# 🚀 Quick Start Guide - Flask Backend with Social Media

## ⚠️ SSL Certificate Issue (macOS)

Your Mac has an SSL certificate issue preventing pip from installing packages. This is common and easy to fix!

---

## 🔧 Fix SSL Issue (Choose ONE method)

### **Method 1: Automatic Fix (Easiest)**

Run the setup script I created:

```bash
cd ~/flaskbackend
bash setup_and_run.sh
```

This will:
- ✅ Fix SSL certificates
- ✅ Create virtual environment
- ✅ Install all packages
- ✅ Get you ready to run!

---

### **Method 2: Manual Fix**

If the automatic script doesn't work, try these commands in your terminal:

```bash
cd ~/flaskbackend

# Fix SSL certificates (macOS)
/Applications/Python\ 3.*/Install\ Certificates.command

# OR if that doesn't exist:
pip3 install --upgrade certifi

# Then continue with setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### **Method 3: Bypass SSL (Quick but less secure)**

Only use this if the above don't work:

```bash
cd ~/flaskbackend
python3 -m venv venv
source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 🎯 After Setup - Running Your Backend

Once packages are installed, run the backend:

### **Option A: Use the Quick Run Script**

```bash
cd ~/flaskbackend
bash run_backend.sh
```

### **Option B: Manual Run**

```bash
cd ~/flaskbackend
source venv/bin/activate  # Activate virtual environment
python main.py             # Start Flask
```

---

## ✅ Testing Your Backend

Once the backend is running, you should see:

```
* Running on http://0.0.0.0:8587
* Running on http://127.0.0.1:8587
```

### **Test the Social Media API:**

Open a new terminal and run:

```bash
# Should return authentication error (meaning API is working!)
curl http://localhost:8587/api/post/all
```

Expected response:
```json
{"message": "Token is missing"}
```

This means your API is working! 🎉

---

## 📱 Access Social Media in Browser

1. **Start your backend**: `bash run_backend.sh`
2. **Start your frontend** (in another terminal)
3. **Login** at your frontend login page
4. **Go to** `/social-media` route
5. **Create your first post!**

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

**Fix:** Activate the virtual environment first:
```bash
source venv/bin/activate
python main.py
```

### "pip: command not found"

**Fix:** Use pip3 instead:
```bash
pip3 install -r requirements.txt
```

### "Permission denied: ./setup_and_run.sh"

**Fix:** Make it executable:
```bash
chmod +x setup_and_run.sh run_backend.sh
bash setup_and_run.sh
```

### SSL Certificate Errors Continue

**Fix:** Reinstall Python from python.org and run the certificate installer:
```bash
# After reinstalling Python
/Applications/Python\ 3.*/Install\ Certificates.command
```

---

## 📊 Database Auto-Creation

The posts database table will be created **automatically** when you run `main.py` for the first time!

You'll see your database file at:
```
~/flaskbackend/instance/volumes/
```

---

## 🎯 What You Get

Once running, your backend provides:

- ✅ **8 Social Media API Endpoints**
- ✅ **JWT Authentication**
- ✅ **Posts with Replies (Threaded Comments)**
- ✅ **Grade Tracking**
- ✅ **User Authorization**
- ✅ **SQLite Database**

---

## 🚀 Next Steps After Backend is Running

1. **Copy frontend files to your pages repo:**
   ```bash
   cp ~/flaskbackend/Social\ Media/*.md ~/pages/navigation/social_media/
   ```

2. **Test the API** with curl or Postman

3. **Login to frontend** and visit `/social-media`

4. **Create your first post!** 🎉

---

## 💡 Pro Tips

- **Keep virtual environment activated** while developing
- **Backend runs on port 8587** by default
- **Frontend should point to** `http://localhost:8587`
- **Check `SOCIAL_MEDIA_SETUP.md`** for full documentation

---

## 🆘 Still Stuck?

If you're still having issues:

1. **Check Python version**: `python3 --version` (should be 3.7+)
2. **Check if virtual environment exists**: `ls venv/`
3. **Check error messages** in terminal carefully
4. **Try the SSL bypass method** (Method 3 above)

---

## ✨ You're Almost There!

Just run:
```bash
bash setup_and_run.sh
```

And your backend will be ready! 🚀

