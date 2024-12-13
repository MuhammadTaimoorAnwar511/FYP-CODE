import React from "react";
import { Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import BTCLogo from "./BTCLogo";

// Import multiple images
import Pic0 from "../../Images/cyberpunk-bitcoin-illustration.jpg";
import Pic1 from "../../Images/Pic1.png";
import Pic2 from "../../Images/Pic2.png";
import Pic3 from "../../Images/Pic3.png";
import Pic4 from "../../Images/Pic4.png";
import Pic5 from "../../Images/Pic5.png";
import Pic6 from "../../Images/Pic6.png";
import Pic7 from "../../Images/Pic7.png";
import Pic8 from "../../Images/Pic8.png";

// Function to select a random image
const getRandomImage = () => {
  const images = [Pic0, Pic1, Pic2, Pic3, Pic4, Pic5, Pic6, Pic7, Pic8];
  return images[Math.floor(Math.random() * images.length)];
};

const Hero = () => {
  const RandImage = getRandomImage(); // Get a random image
  const navigate = useNavigate(); // React Router's navigation hook

  return (
    <section
      id="home"
      className="min-h-screen flex flex-col md:flex-row items-center justify-between bg-gray-900 text-white"
    >
      {/* Left Content */}
      <div className="md:w-1/2 p-8 text-center md:text-left">
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Automated Crypto Trading Bot
        </h1>
        <p className="mt-4 text-lg text-gray-300">
          Connect with top exchanges and let our AI-powered bot trade 24/7, emotionless and efficient.
        </p>
        <div className="mt-6 space-x-4">
          <Button
            variant="contained"
            className="bg-blue-500 hover:bg-blue-600"
            onClick={() => navigate('/register')} // Navigate to Sign Up page
          >
            Get Started
          </Button>
        </div>
      </div>

      {/* Right Content */}
      <div className="md:w-1/2 h-96 flex items-center justify-center">
        <BTCLogo image={RandImage} />
      </div>
    </section>
  );
};

export default Hero;
