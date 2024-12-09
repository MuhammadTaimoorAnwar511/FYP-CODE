import React from "react";

const AboutUs = () => {
  return (
    <section id="about" className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto text-center px-6">
        <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          About Us
        </h2>
        <p className="mt-6 text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
          We are a team of passionate developers, data scientists, and crypto enthusiasts dedicated to revolutionizing automated trading in the cryptocurrency market.
        </p>
        <p className="mt-4 text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
          Our mission is to provide accessible, efficient, and intelligent trading solutions that level the playing field for all investors.
        </p>
      </div>
    </section>
  );
};

export default AboutUs;
