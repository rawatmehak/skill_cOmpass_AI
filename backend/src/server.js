import app from "./app.js";
import dotenv from "dotenv";
import mongoose from "mongoose";

dotenv.config();
const PORT = process.env.PORT || 3000;
const mongoUri = process.env.MONGODB_URI || process.env.MONGO_URI;

if (!mongoUri) {
    console.error("Missing MongoDB connection string. Set MONGODB_URI or MONGO_URI in backend/.env");
    process.exit(1);
}

mongoose.connect(mongoUri)
.then(()=>{
    console.log("MongoDb connected");
    app.listen(PORT,()=>{
        console.log(`Server running on http://localhost:${PORT}`);
    });
})
.catch(err=>console.log("MongoDB connection error",err));
