import React from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  MenuItem,
} from "@mui/material";
import GoogleIcon from "../Images/googleIcon.png";
import cryptoTradeBot from "../Images/tradeBotT.png";
import FlipLogo from "../Components/LoginandSignup/FlipLogo";
import walletIcon from "../Images/walletIcon.png";

const SignupPage = () => {
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
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#000000",
          overflow: "hidden", // Prevent overflow
          padding: { xs: "1.5rem", md: "2rem" }, // Adjust padding for smaller screens
        }}
      >
        <Box
          sx={{
            width: "90%",
            maxWidth: { xs: "25rem", md: "25rem", lg:"35rem" },
            // maxHeight: { xs: "25rem", md: "25rem", lg:"45rem" },
            textAlign: "center",
            padding: "2rem",
            backgroundColor: "#FFFFFF",
            borderRadius: "16px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            outline: "2px solid #16A647",
            // height: "auto",
            // overflow: "hidden", // Prevent overflow
            // overflowY: "auto",
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
            Create Your Account
          </Typography>
          <Typography
            variant="subtitle1"
            sx={{
              color: "#666666",
              mb: 3,
              fontSize: { xs: "0.9rem", md: "1rem" }, // Adjust font size
            }}
          >
            Sign up to get started
          </Typography>

          {/* Continue with Google */}
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
            Continue with Google
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
              Or sign up with
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

          {/* Username Input */}
          <TextField
            fullWidth
            label="Username"
            variant="outlined"
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

          {/* Email Input */}
          <TextField
            fullWidth
            label="Email"
            variant="outlined"
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

          {/* Country Dropdown */}
          <TextField
            select
            fullWidth
            label="Country"
            variant="outlined"
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
          >
            <MenuItem value="USA">USA</MenuItem>
            <MenuItem value="India">India</MenuItem>
            <MenuItem value="Canada">Canada</MenuItem>
            <MenuItem value="UK">UK</MenuItem>
          </TextField>

          {/* Password Input */}
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
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

          {/* Confirm Password Input */}
          <TextField
            fullWidth
            label="Confirm Password"
            type="password"
            variant="outlined"
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

          {/* Signup Button */}
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
            Sign Up
          </Button>
        </Box>
      </Box>
      {/* Right Half */}
    <Box
    sx={{
        flex: 1,
        backgroundImage: `url(${cryptoTradeBot})`,
        backgroundSize: "cover",
        backgroundPosition: "cover",
        display: { xs: "none", sm: "block" }, // Hide on small devices
    }}
    ></Box>
    </Box>
  );
};

export default SignupPage;