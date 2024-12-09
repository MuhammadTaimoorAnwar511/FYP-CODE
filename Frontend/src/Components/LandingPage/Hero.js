import React from "react";
import { Button } from "@mui/material";
import BTCLogo from "./BTCLogo";
import btcImage from "../../Images/cyberpunk-bitcoin-illustration.jpg"; 

const Hero = () => {
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
          <Button variant="contained" className="bg-blue-500 hover:bg-blue-600">
            Get Started
          </Button>
        </div>
      </div>

      {/* Right Content */}
      <div className="md:w-1/2 h-96 flex items-center justify-center">
        <BTCLogo image={btcImage} /> {/* Pass the image prop here */}
      </div>
    </section>
  );
};

export default Hero;
