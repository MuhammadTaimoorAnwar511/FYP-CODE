import React, { useState } from 'react';
import { Menu, MenuItem, IconButton } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

const Navbar2 = ({ theme, setTheme }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const navigate=useNavigate()

  const navItems = ['Home', 'Features', 'Exchanges', 'Coins', 'About', 'Contact'];

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
      <Link to="/" className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
          Crypto TradeBot
        </Link>
        <nav className="hidden md:flex space-x-6">
          {navItems.map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-blue-400">
              {item}
            </a>
          ))}
        </nav>
        <div className="flex items-center space-x-4">
          <IconButton
            onClick={handleUserMenuOpen}
            size="large"
            edge="end"
            color="inherit"
          >
            <AccountCircleIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleUserMenuClose}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={()=>{navigate("/Journal")}}>Dashboard</MenuItem>
            <MenuItem onClick={handleUserMenuClose}>Home</MenuItem>
            <MenuItem onClick={()=>{navigate("/Profile")}}>Profile</MenuItem>
            <MenuItem onClick={handleUserMenuClose}>Logout</MenuItem>
          </Menu>
        </div>
      </div>
    </header>
  );
};

export default Navbar2;