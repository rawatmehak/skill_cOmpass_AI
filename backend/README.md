# 🧠 SkillCompass AI — Backend

**SkillCompass AI** is an intelligent career guidance platform that analyzes a user's skills, predicts the best-fit career paths, and provides real-time insights about job market trends, skill demand, and growth.  
This repository contains the **backend API**, built with Node.js, Express, and MongoDB.

---

## 🚀 Features

✅ **Authentication System**
- Secure JWT-based login & registration  
- Password hashing using bcrypt  
- Token-based route protection

✅ **User Skill Management**
- Add and update personal skills with proficiency ratings  
- Store skill data in MongoDB for recommendations

✅ **Career Recommendation Engine**
- AI-style logic that compares user skills with role requirements  
- Suggests best-fit role, missing skills, and personalized learning roadmap  
- Saves recommendation history automatically

✅ **Trending Skills API**
- Lists top 5 skills based on current demand and growth  
- Useful for market-aware upskilling suggestions

✅ **Career Insights**
- Provides salary range, saturation level, job growth rate, and key trends by role  

✅ **Job Matching**
- Shows job openings per role  
- Calculates skill–fit score and sorts jobs accordingly

✅ **Centralized Error Handling**
- Unified error format for all routes  
- Async error management using `asyncHandler` middleware

✅ **MongoDB Integration**
- All user and recommendation data persistently stored  
- Easily scalable with Mongoose schema models

---

## ⚙️ Tech Stack

- **Node.js** — Runtime environment  
- **Express.js** — Web framework  
- **MongoDB + Mongoose** — Database & ODM  
- **JWT (jsonwebtoken)** — Authentication  
- **bcryptjs** — Password hashing  
- **dotenv** — Environment variable management  
- **Nodemon** — Auto-reload during development  

---

## 📁 Folder Structure

backend/
│
├── src/
│ ├── controllers/ # All controller logic (Auth, User, Jobs, Skills, Insights)
│ ├── routes/ # Route definitions for each module
│ ├── models/ # Mongoose models (User, Recommendation)
│ ├── middleware/ # Auth, asyncHandler, errorHandler
│ ├── data/ # Static data files (roles.json, skills.json, roleSkillMap.js)
│ └── server.js # App entry point
│
├── .env # Environment variables
├── package.json
└── README.md

## 🧰 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/SkillCompass-AI.git
cd SkillCompass-AI/backend

2️⃣ Install Dependencies
npm install

3️⃣ Create .env File

In the root of backend/, create a .env file:

PORT=3000
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_secret_key

4️⃣ Run the Server
npm run dev

Server will start at:
👉 http://localhost:3000