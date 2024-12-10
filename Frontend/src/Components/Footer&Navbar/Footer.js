import React from 'react';
import {
  Facebook,
  Twitter,
  Instagram,
  LinkedIn,
  Email,
  Phone,
} from '@mui/icons-material';

const Footer = () => {
  const navItems = ['About Us', 'Services', 'Blog', 'Careers', 'Contact'];

  return (
    <footer
      className="bg-black text-white border-t-2 border-gray-500"
      style={{
        background: "radial-gradient(ellipse, #4B5563, #1F2937, #000)",
      }}
    >
      <div className="container mx-auto py-12 px-6">
        {/* Top Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {/* About Section */}
          <div>
            <h3 className="text-3xl font-bold text-blue-400 mb-4">
              Crypto TradeBot
            </h3>
            <p className="text-gray-300 leading-relaxed">
              Your trusted partner in cryptocurrency trading. Stay ahead with
              real-time insights, powerful tools, and an intuitive platform for
              crypto enthusiasts.
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="text-2xl font-bold text-blue-400 mb-4">
              Quick Links
            </h3>
            <ul className="space-y-3">
              {navItems.map((item) => (
                <li key={item}>
                  <a
                    href={`#${item.toLowerCase().replace(' ', '-')}`}
                    className="hover:text-blue-400 transition-colors duration-300"
                  >
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Section */}
          <div>
            <h3 className="text-2xl font-bold text-blue-400 mb-4">
              Get in Touch
            </h3>
            <div className="space-y-3">
              <p className="flex items-center">
                <Email className="mr-3 text-blue-400" />
                support@cryptotradebot.com
              </p>
              <p className="flex items-center">
                <Phone className="mr-3 text-blue-400" />
                +1 (123) 456-7890
              </p>
            </div>
            <div className="flex space-x-5 mt-5">
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:scale-110 transform transition-all duration-300"
              >
                <Facebook fontSize="large" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:scale-110 transform transition-all duration-300"
              >
                <Twitter fontSize="large" />
              </a>
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-pink-500 hover:scale-110 transform transition-all duration-300"
              >
                <Instagram fontSize="large" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:scale-110 transform transition-all duration-300"
              >
                <LinkedIn fontSize="large" />
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-700 mt-10"></div>

        {/* Bottom Section */}
        <div className="mt-10 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400">
            © {new Date().getFullYear()} Crypto TradeBot. All rights reserved.
          </p>
          <div className="flex space-x-5 mt-4 md:mt-0">
            <a
              href="/privacy-policy"
              className="text-gray-400 hover:text-blue-400 transition-colors duration-300"
            >
              Privacy Policy
            </a>
            <a
              href="/terms-of-service"
              className="text-gray-400 hover:text-blue-400 transition-colors duration-300"
            >
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;