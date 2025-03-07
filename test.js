import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import GoogleIcon from "../Images/googleIcon.png";
import cryptoTradeBot from "../Images/tradeBotT.png";
import FlipLogo from "../Components/LoginandSignup/FlipLogo";
import walletIcon from "../Images/walletIcon.png";

const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:5000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Login failed");
      }

      // Store the access token in localStorage
      localStorage.setItem("accessToken", data.access_token);
      
      // Redirect to market overview
      navigate("/MarketOverview");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        width: "100%",
        fontFamily: "Poppins, sans-serif",
      }}
    >
      {/* Left Half */}
      <Box
        sx={{
          flex: 1,
          backgroundImage: `url(${cryptoTradeBot})`,
          backgroundSize: "cover",
          backgroundPosition: "cover",
          display: { xs: "none", sm: "block" },
        }}
      ></Box>

      {/* Right Half */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#000000",
          overflow: "hidden",
          padding: { xs: "1.5rem", md: "2rem" },
        }}
      >
        <Box
          component="form"
          onSubmit={handleLogin}
          sx={{
            width: "90%",
            maxWidth: {xs: "25rem", md: "25rem", lg: "35rem"},
            textAlign: "center",
            padding: "2rem",
            backgroundColor: "#FFFFFF",
            borderRadius: "16px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            outline: "2px solid #16A647",
            mx: "auto",
          }}
        >
          {/* Logo */}
          <FlipLogo image={walletIcon} />
          
          {/* Error Message */}
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          {/* Welcome Text */}
          <Typography
            variant="h4"
            sx={{
              color: "#111111",
              fontWeight: "bold",
              mb: 1,
              fontSize: { xs: "1.5rem", md: "2rem" },
            }}
          >
            Welcome Back
          </Typography>
          <Typography
            variant="subtitle1"
            sx={{
              color: "#666666",
              mb: 3,
              fontSize: { xs: "0.9rem", md: "1rem" },
            }}
          >
            Login into your account
          </Typography>

          {/* Google Login (unchanged) */}

          {/* Form Fields */}
          <TextField
            required
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            variant="outlined"
            sx={{
              mb: 2,
              "& .MuiOutlinedInput-root": {
                borderRadius: "10px",
                "& fieldset": { borderColor: "#CCCCCC" },
                "&:hover fieldset": { borderColor: "#999999" },
                "&.Mui-focused fieldset": { borderColor: "#1976D2" },
              },
            }}
          />

          <TextField
            required
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            variant="outlined"
            sx={{
              mb: 3,
              "& .MuiOutlinedInput-root": {
                borderRadius: "10px",
                "& fieldset": { borderColor: "#CCCCCC" },
                "&:hover fieldset": { borderColor: "#999999" },
                "&.Mui-focused fieldset": { borderColor: "#1976D2" },
              },
            }}
          />

          {/* Remember Me (unchanged) */}

          {/* Login Button */}
          <Button
            type="submit"
            variant="contained"
            fullWidth
            sx={{
              backgroundColor: "#1976D2",
              color: "#FFFFFF",
              ":hover": { backgroundColor: "#115293" },
              // ... rest of styles
            }}
          >
            Log In
          </Button>

          {/* Sign Up Link */}
          <Typography sx={{ mt: 3, color: "#666666" }}>
            Don’t have an account?{" "}
            <Link
              component="button"
              onClick={() => navigate("/register")}
              sx={{ color: "#1976D2", fontWeight: "bold" }}
            >
              Sign up!
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default LoginPage;