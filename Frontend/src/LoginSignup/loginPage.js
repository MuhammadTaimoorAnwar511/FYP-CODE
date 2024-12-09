import React from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
} from "@mui/material";
import GoogleIcon from "../Images/googleIcon.png";
import cryptoTradeBot from "../Images/tradeBotT.png";
import FlipLogo from "../Components/LoginandSignup/FlipLogo";
import walletIcon from "../Images/walletIcon.png";

const LoginPage = () => {
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
          display: { xs: "none", sm: "block" }, // Hide on small devices
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
          overflow: "hidden", // Prevent overflow
          padding: { xs: "1.5rem", md: "2rem" }, // Adjust padding on smaller screens
        }}
      >
        <Box
          sx={{
            width: "90%",
            maxWidth: {xs: "25rem", md: "25rem", lg: "35rem"},
            textAlign: "center",
            padding: "2rem",
            backgroundColor: "#FFFFFF",
            borderRadius: "16px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            outline: "2px solid #16A647",
            mx: "auto", // Center the box horizontally
          }}
        >
          {/* Logo */}
          <FlipLogo image={walletIcon} />
          {/* Welcome Text */}
          <Typography
            variant="h4"
            sx={{
              color: "#111111",
              fontWeight: "bold",
              mb: 1,
              fontSize: { xs: "1.5rem", md: "2rem" }, // Responsive font size
            }}
          >
            Welcome Back
          </Typography>
          <Typography
            variant="subtitle1"
            sx={{
              color: "#666666",
              mb: 3,
              fontSize: { xs: "0.9rem", md: "1rem" }, // Adjust font size
            }}
          >
            Login into your account
          </Typography>

          {/* Login with Google */}
          <Button
            variant="outlined"
            fullWidth
            sx={{
              mb: 3,
              backgroundColor: "#FFFFFF",
              borderRadius: "8px",
              color: "#333333",
              borderColor: "#20DC49",
              textTransform: "none",
              fontWeight: "bold",
              fontSize: "1rem",
              padding: "12px 16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              overflow: "hidden", // Prevent overflow
              gap: "8px",
              ":hover": {
                borderColor: "#16A647",
                backgroundColor: "#f9f9f9",
              },
            }}
          >
            <img
              src={GoogleIcon}
              alt="Google Icon"
              style={{
                width: "20px",
                height: "20px",
              }}
            />
            Login with Google
          </Button>

          {/* Divider */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mb: 3,
            }}
          >
            <Box
              sx={{
                flex: 1,
                height: "1px",
                backgroundColor: "#DBDBDB",
                marginRight: "8px",
              }}
            ></Box>
            <Typography
              sx={{
                color: "#666666",
                textAlign: "center",
                fontSize: "0.9rem",
                fontWeight: "500",
              }}
            >
              Or continue with
            </Typography>
            <Box
              sx={{
                flex: 1,
                height: "1px",
                backgroundColor: "#DBDBDB",
                marginLeft: "8px",
              }}
            ></Box>
          </Box>

          {/* Email Input */}
          <TextField
            fullWidth
            label="Email"
            variant="outlined"
            InputProps={{
              sx: {
                height: "55px",
                borderRadius: "10px",
                backgroundColor: "#FFFFFF",
              },
            }}
            sx={{
              mb: 2,
              "& .MuiOutlinedInput-root": {
                borderRadius: "10px",
                "& fieldset": {
                  borderColor: "#CCCCCC",
                },
                "&:hover fieldset": {
                  borderColor: "#999999",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#1976D2",
                },
              },
            }}
          />

          {/* Password Input */}
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
            InputProps={{
              sx: {
                height: "55px",
                borderRadius: "10px",
                backgroundColor: "#FFFFFF",
              },
            }}
            sx={{
              mb: 3,
              "& .MuiOutlinedInput-root": {
                borderRadius: "10px",
                "& fieldset": {
                  borderColor: "#CCCCCC",
                },
                "&:hover fieldset": {
                  borderColor: "#999999",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#1976D2",
                },
              },
            }}
          />

          {/* Remember Me */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 3,
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
              }}
            >
              <input
                type="checkbox"
                id="rememberMe"
                style={{
                  marginRight: "8px",
                  transform: "scale(1.2)",
                }}
              />
              <Typography
                variant="body2"
                sx={{
                  color: "#666666",
                }}
              >
                Remember me
              </Typography>
            </Box>
          </Box>

          {/* Login Button */}
          <Button
            variant="contained"
            fullWidth
            sx={{
              backgroundColor: "#1976D2",
              color: "#FFFFFF",
              textTransform: "none",
              fontWeight: "bold",
              fontSize: "1rem",
              padding: "12px 16px",
              borderRadius: "8px",
              ":hover": {
                backgroundColor: "#115293",
              },
            }}
          >
            Log In
          </Button>

          {/* Sign Up Link */}
          <Typography
            sx={{
              mt: 3,
              color: "#666666",
              textAlign: "center",
            }}
          >
            Don’t have an account?{" "}
            <Link href="#" variant="body2" sx={{ color: "#1976D2", fontWeight: "bold" }}>
              Sign up!
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default LoginPage;