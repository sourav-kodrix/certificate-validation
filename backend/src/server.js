require("dotenv").config();

const express = require("express");
const cors = require("cors");
const helmet = require("helmet");

const connectDB = require("./config/db");
const certificateRoutes = require("./routes/certificateRoutes");
const errorHandler = require("./middleware/errorMiddleware");

const app = express();

app.set("trust proxy", 1);

connectDB();

app.use(helmet());

app.use(
    cors({
        origin: process.env.CLIENT_URL,
    })
);

app.use(express.json());

app.use("/api/certificates", certificateRoutes);

app.get("/api/health", (req, res) => {
    res.json({
        success: true,
        message: "Certificate API is running",
    });
});

app.use(errorHandler);

const PORT = process.env.PORT || 5000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});