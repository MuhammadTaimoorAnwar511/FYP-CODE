import React, { useState } from "react";
import { Box } from "@mui/material";

const BTCLogo = ({ image }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        mb: 2,
        perspective: "1000px", // Enable 3D perspective for the flip effect
      }}
      onMouseEnter={() => setIsHovered(true)} // Trigger hover state
      onMouseLeave={() => setIsHovered(false)} // Reset hover state
    >
      <Box
        component="img"
        src={image}
        alt="BTC Logo"
        sx={{
          width: "500px",
          height: "500px",
          transition: "transform 0.6s", // Smooth animation
          transformStyle: "preserve-3d", // Preserve 3D effect during the flip
          transform: isHovered ? "rotateY(360deg)" : "rotateY(0deg)", // Flip on hover
        }}
      />
    </Box>
  );
};

export default BTCLogo;