import React, { useState } from "react";
import { Menu, MenuItem, IconButton } from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import { Link, useNavigate } from "react-router-dom";

const Navbar2 = ({ theme, setTheme }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const navigate = useNavigate();

  // Define the navigation items with their corresponding routes
  const navItems = [
    { label: "Market Overview", path: "/MarketOverview" },
    { label: "Chart", path: "/Chart" },
    { label: "Journal", path: "/Journal" },
    { label: "Profile", path: "/Profile" },
  ];

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        {/* Logo */}
        <Link
          to="/"
          className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400"
        >
          Crypto TradeBot
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex space-x-6">
          {navItems.map((item) => (
            <Link
              key={item.label}
              to={item.path}
              className="hover:text-blue-400 transition-colors duration-300"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User Menu */}
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
              vertical: "top",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
          >
            {navItems.map((item) => (
              <MenuItem
                key={item.label}
                onClick={() => {
                  navigate(item.path);
                  handleUserMenuClose(); // Close menu after navigation
                }}
              >
                {item.label}
              </MenuItem>
            ))}
            <MenuItem
              onClick={() => {
                navigate("/");
                handleUserMenuClose(); // Close menu after navigation
              }}
            >
              Log Out
            </MenuItem>
          </Menu>
        </div>
      </div>
    </header>
  );
};

export default Navbar2;
