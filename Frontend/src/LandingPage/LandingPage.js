import React, { useState } from "react";
import Navbar from "../Components/LandingPage/Landing_Navbar";
import Hero from "../Components/LandingPage/Hero";
import Features from "../Components/LandingPage/Features";
import Exchanges from "../Components/LandingPage/Exchanges";
import CoinLogos from "../Components/LandingPage/CoinLogos";
import AboutUs from "../Components/LandingPage/AboutUs";
import ContactForm from "../Components/LandingPage/ContactForm";

function LandingPage() {
  const [theme, setTheme] = useState("dark");

  return (
    <div
      className={`min-h-screen ${
        theme === "dark" ? "bg-gray-900 text-white" : "bg-white text-black"
      }`}
    >
      <Navbar theme={theme} setTheme={setTheme} />
      <Hero />
      <Features />
      <Exchanges />
      <CoinLogos />
      <AboutUs /> 
      <ContactForm />
    </div>
  );
}

export default LandingPage;
