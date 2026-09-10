# 🛡️ FaceTrack — Facial Recognition Attendance System

A professional, cloud-ready attendance system that uses facial recognition
to check people in, built with **Streamlit**, **OpenCV**, and **MongoDB Atlas**.

## ✨ Features

- 📊 Live dashboard with attendance stats and a 7-day trend chart
- 🧾 Register people by capturing multiple face samples via webcam
- 🎯 Mark attendance automatically through face recognition (once per day per person)
- 📁 Filterable attendance records with CSV export
- 👥 Manage (search / delete) registered people
- 🎨 Custom professional UI theme (no design skills required to run it)
- ☁️ Fully deployable for free on Streamlit Community Cloud

## 🧱 Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Frontend/UI    | Streamlit                                |
| Face Detection | OpenCV Haar Cascade                      |
| Face Recognition | OpenCV LBPH (Local Binary Patterns)    |
| Database       | MongoDB Atlas (cloud, free tier works)   |
| Hosting        | Streamlit Community Cloud                |

> **Why LBPH instead of `face_recognition`/dlib?**
> `dlib`-based libraries require compiling C++ code and often fail or time
> out on Streamlit Cloud's free build environment. OpenCV's LBPH recognizer
> ships as a pre-built wheel (`opencv-contrib-python-headless`), installs
> instantly, and is accurate enough for classroom/office-scale attendance.

## 📁 Project Structure

```
face-attendance-app/
├── app.py                        # Main Streamlit app
├── requirements.txt              # Python dependencies
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml               # Theme configuration
│   └── secrets.toml.example      # Template — copy to secrets.toml locally
└── utils/
    ├── __init__.py
    ├── database.py                # MongoDB Atlas CRUD functions
    ├── face_utils.py               # Face detection & recognition
    └── styles.py                   # Custom CSS
```

---

## 🚀 Part 1 — Set Up MongoDB Atlas

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) and create a free account.
2. Create a **free M0 cluster** (any cloud provider/region is fine).
3. Under **Database Access**, create a database user with a username and password.
4. Under **Network Access**, click **Add IP Address** → **Allow Access from Anywhere** (`0.0.0.0/0`)
   — this is required so Streamlit Cloud's servers can reach your cluster.
5. Click **Connect** on your cluster → **Drivers** → copy the connection string.
   It looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<username>` and `<password>` with your actual database user credentials.

No need to manually create collections — `users` and `attendance` are created
automatically the first time data is written.

---

## 💻 Part 2 — Run Locally

```bash
# 1. Clone or download this project, then enter the folder
cd face-attendance-app

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your MongoDB connection string
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real MONGO_URI

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Part 3 — Deploy to GitHub + Streamlit Community Cloud

### Step 1: Push to GitHub

```bash
cd face-attendance-app
git init
git add .
git commit -m "Initial commit: FaceTrack attendance system"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

> ✅ `.gitignore` already excludes `secrets.toml` so your real MongoDB
> credentials are never pushed to GitHub.

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Advanced settings** → **Secrets**, and paste:
   ```toml
   MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   MONGO_DB_NAME = "facetrack_db"
   ```
5. Click **Deploy**. Streamlit Cloud will install `requirements.txt` and launch your app.
6. You'll get a public URL like:
   ```
   https://<your-app-name>.streamlit.app
   ```

### Updating the live app later

Any time you push new commits to the `main` branch on GitHub, Streamlit Cloud
automatically redeploys the app — no manual steps needed.

---

## ⚙️ Configuration Notes

- **Recognition sensitivity**: Adjust `RECOGNITION_THRESHOLD` in
  `utils/face_utils.py` (lower = stricter matching, higher = more lenient).
  Default is `75`.
- **Minimum face samples**: Registration requires at least 3 samples for
  reasonable accuracy; you can raise this in `app.py` for stricter enrollment.
- **Camera access**: `st.camera_input` requires the browser to grant camera
  permission and works over HTTPS (Streamlit Cloud serves HTTPS by default).

## 🔒 Security Notes

- Never commit `.streamlit/secrets.toml` — it's already git-ignored.
- Consider restricting MongoDB Atlas Network Access to specific IPs in
  production rather than `0.0.0.0/0` if you have a known deployment IP range.
- Face image samples are stored as base64-encoded grayscale images in
  MongoDB. For stricter privacy/compliance needs, consider encrypting these
  fields at rest or storing only derived features.

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| "Could not connect to MongoDB Atlas" | Double-check `MONGO_URI`, password, and that Network Access allows `0.0.0.0/0` |
| Camera not opening | Ensure browser has camera permission; try Chrome/Edge |
| Face not recognized | Re-register with more samples in good, even lighting |
| App fails to build on Streamlit Cloud | Confirm `requirements.txt` uses `opencv-contrib-python-headless`, not `opencv-python` |

---

Built with ❤️ using Streamlit, OpenCV, and MongoDB Atlas.
