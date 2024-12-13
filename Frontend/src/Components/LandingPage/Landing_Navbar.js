import React from 'react';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Landing_Navbar = () => {
  const navigate = useNavigate(); // React Router's navigation hook
  const navItems = ['Home', 'Features', 'Exchanges', 'Coins', 'About', 'Contact'];

  return (
    <header className="sticky top-0 z-50 w-full bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
          CryptoBot
        </div>
        <nav className="hidden md:flex space-x-6">
          {navItems.map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-blue-400">
              {item}
            </a>
          ))}
        </nav>
        <div className="flex items-center space-x-4">
          <Button
            variant="outlined"
            className="hidden md:block"
            onClick={() => navigate('/Login')} // Navigate to Login
          >
            Login
          </Button>
          <Button
            variant="contained"
            className="hidden md:block bg-blue-500 hover:bg-blue-600"
            onClick={() => navigate('/register')} // Navigate to Sign Up
          >
            Sign Up
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Landing_Navbar;
