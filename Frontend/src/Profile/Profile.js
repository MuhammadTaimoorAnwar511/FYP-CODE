import React, { useState, useRef, useEffect } from 'react';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'; 
import CheckIcon from '@mui/icons-material/Check';
import SearchIcon from '@mui/icons-material/Search';
import Navbar2 from "../Components/Footer&Navbar/Navbar2"
import Footer from "../Components/Footer&Navbar/Footer"

const API_HOST = process.env.REACT_APP_API_HOST;
const API_PORT = process.env.REACT_APP_API_PORT;
const BASE_URL = `http://${API_HOST}:${API_PORT}`;

function ProfilePage() {
  
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedExchange, setSelectedExchange] = useState('OKX');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [phrase, setPhrase] = useState('');

  const [connectionStatus, setConnectionStatus] = useState(null);
  
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);
 
  const exchanges = [
    { name: 'OKX', icon: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSu0QUtkN8EjVWEgvIfiQ5G7Wq833qsFYzL8g&s' },
    { name: 'Binance (Coming soon)', icon: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsKz71ieYKv2qQ_qixqjTeoGJ9rhFWu5q--A&s' },
    { name: 'BYBIT (Coming soon)', icon: 'https://play-lh.googleusercontent.com/SJxOSA2a2WY2RYQKv99kKCQVVqA5tmgw2VHn_YY0gL4riv7eDDjZ46X5_6Jge-Ur8uo' },
  ];

  // Filter exchanges based on search term
  const filteredExchanges = exchanges.filter((ex) =>
    ex.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExchangeSelect = (exchange) => {
    setSelectedExchange(exchange.name);
    setApiKey('');
    setApiSecret('');
    setPhrase('')
    setConnectionStatus(null);
    setDropdownOpen(false);
    setFocusedIndex(-1);
  };
  
  const testConnection = async () => {
    if (!apiKey || !apiSecret || !phrase) {
      setConnectionStatus('error');
      setTimeout(() => setConnectionStatus(null), 3000);
      return;
    }
    
    try {
      const response = await fetch(`${BASE_URL}/exchange/TestConnection`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          api_key: apiKey,
          api_secret: apiSecret,
          passphrase: phrase,
        }),
      });
  
      const data = await response.json();
  
      if (data.success) {
        setConnectionStatus('success');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      console.error("Error testing connection:", error);
      setConnectionStatus('error');
    }
  
    setTimeout(() => setConnectionStatus(null), 3000);
  };

  const saveConnection = async () => {
    const token = localStorage.getItem('access_token');

    console.log("Selected Exchange:", selectedExchange);
    console.log("API Key:", apiKey);
    console.log("Secret Key:", apiSecret);
    console.log("Secret Phrase:", phrase);

    try {
        const response = await fetch(`${BASE_URL}/user/update-feilds`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                selectedExchange,
                apiKey,
                apiSecret,
                phrase
            })
        });

        const data = await response.json();
        if (response.ok) {
            alert("Exchange details updated successfully!");
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error("Error updating exchange details:", error);
        alert("Something went wrong!");
    }
};

  // Close dropdown when clicked outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownOpen &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !buttonRef.current.contains(event.target)
      ) {
        setDropdownOpen(false);
        setFocusedIndex(-1);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  // Keyboard navigation
  const handleKeyDown = (e) => {
    if (!dropdownOpen) return;

    const maxIndex = filteredExchanges.length - 1;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex((prev) => (prev < maxIndex ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex((prev) => (prev > 0 ? prev - 1 : maxIndex));
        break;
      case 'Enter':
        e.preventDefault();
        if (focusedIndex >= 0 && filteredExchanges[focusedIndex]) {
          handleExchangeSelect(filteredExchanges[focusedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setDropdownOpen(false);
        setFocusedIndex(-1);
        break;
      default:
        break;
    }
  };

  useEffect(() => {
    if (dropdownOpen) {
      document.addEventListener('keydown', handleKeyDown);
    } else {
      document.removeEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [dropdownOpen, focusedIndex, filteredExchanges]);


  // Fetch user profile data on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
      const token = localStorage.getItem('access_token'); 
      if (!token) {
        throw new Error('No authentication token found');
      }
        const response = await fetch(`${BASE_URL}/user/profile`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch profile data');
        }
        
        const data = await response.json();
        setUserData(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // Update the Hero Section to use fetched data
  const renderProfileInfo = () => {
    if (loading) {
      return (
        <div className="space-y-2">
          <div className="h-8 bg-gray-700 rounded animate-pulse w-48"></div>
          <div className="h-4 bg-gray-700 rounded animate-pulse w-64"></div>
          <div className="h-4 bg-gray-700 rounded animate-pulse w-32"></div>
        </div>
      );
    }

    if (error || !userData) {
      return (
        <div className="text-red-400">
          <ErrorOutlineIcon className="mr-2" />
          Error loading profile data
        </div>
      );
    }

    return (
    <>
      <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent animate-pulse-slow">
        {userData?.username}
      </h1>
      {userData?._id && <p className="text-gray-300 mt-1 text-sm">{userData._id}</p>}
      {userData?.email && <p className="text-gray-300 mt-1 text-sm">{userData.email}</p>}
      {userData?.country && <p className="text-gray-300 mt-1 text-sm">{userData.country}</p>}
      {userData?.exchange && <p className="text-gray-300 mt-1 text-sm">{userData.exchange}</p>}
      {userData?.api_key && <p className="text-gray-300 mt-1 text-sm">{userData.api_key}</p>}
      {userData?.secret_key && <p className="text-gray-300 mt-1 text-sm">{userData.secret_key}</p>}
      {userData?.secret_phrase && <p className="text-gray-300 mt-1 text-sm">{userData.secret_phrase}</p>}
    </>
    );
  };

 ///
 
   const [subscriptions, setSubscriptions] = useState({});
   const [isBotModalOpen, setIsBotModalOpen] = useState(false);
   const [isUnsubscribeModalOpen, setIsUnsubscribeModalOpen] = useState(false);
   const [selectedBot, setSelectedBot] = useState("");
   const [balance, setBalance] = useState("");
 
   const checkSubscriptionStatus = async (botName) => {
     const response = await fetch(`${BASE_URL}/subscription/status`, {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify({
         user_id: userData?._id,
         bot_name: botName,
       }),
     });
 
     const data = await response.json();
     return data.subscribed;
   };
 
   useEffect(() => {
     const fetchSubscriptions = async () => {
       const botNames = [
         "BTC_USDT",
         "ETH_USDT",
         "BNB_USDT",
         "SOL_USDT",
         "PEPE_USDT",
       ];
 
       let subscriptionStatus = {};
       for (let botName of botNames) {
         const isSubscribed = await checkSubscriptionStatus(botName);
         subscriptionStatus[botName] = isSubscribed;
       }
       setSubscriptions(subscriptionStatus);
     };
 
     if (userData?._id) {
       fetchSubscriptions();
     }
   }, [userData]);
 
   const handleButtonClick = (botName) => {
     setSelectedBot(botName);
     if (subscriptions[botName]) {
       setIsUnsubscribeModalOpen(true);
     } else {
       setIsBotModalOpen(true);
     }
   };
 
   const closeModal = () => {
     setIsBotModalOpen(false);
     setIsUnsubscribeModalOpen(false);
     setSelectedBot("");
     setBalance("");
   };
 
   const handleSubscribe = async () => {
    const response = await fetch(`${BASE_URL}/subscription/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        bot_name: selectedBot,
        user_id: userData?._id,
        balance_allocated: balance,
      }),
    });
  
    const data = await response.json();
    
    // Check if there is an error in the response
    if (data.error) {
      alert(data.error); // Display the error message to the user
    } else if (data.message) {
      setSubscriptions(prev => ({ ...prev, [selectedBot]: true }));
      alert(data.message); // Display the success message
    }
  
    closeModal();
  };
  
 
   const handleUnsubscribe = async () => {
    if (!userData?._id) {
      alert("User ID is missing!");
      return;
    }
  
    const response = await fetch(`${BASE_URL}/subscription/delete/${userData._id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });
  
    const data = await response.json();
  
    if (data.message) {
      setSubscriptions(prev => ({ ...prev, [selectedBot]: false }));
      alert(data.message);
    } else if (data.error) {
      alert(data.error);
    }
  
    closeModal();
  };
  
 ///
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex-none">
        <Navbar2 />
      </div>
      <div className="max-w-7xl mx-auto py-12 px-6">
        {/* Hero Section */}
        <div className="bg-gray-800 rounded-lg p-8 relative overflow-hidden">
          <div className="absolute inset-0 opacity-20 bg-gradient-to-tr from-gray-700 to-gray-900"></div>
          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <div className="relative group">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/User-avatar.svg/2048px-User-avatar.svg.png"
                  alt="User Avatar"
                  className="w-24 h-24 rounded-full border-4 border-blue-500 shadow-[0_0_15px_#3b82f6] transform transition group-hover:scale-105"
                />
              </div>
              <div>
                {renderProfileInfo()}
              </div>
            </div>
          </div>
        </div>

        {/* Exchange Connections Section */}
        <div className="bg-gray-800 rounded-lg p-8 mt-12 relative overflow-hidden min-h-[430px]">
          <div className="absolute inset-0 opacity-20 bg-gradient-to-br from-gray-700 to-gray-900"></div>
          <div className="relative z-10 border-b border-gray-700 pb-4 mb-8">
            <h2 className="text-2xl font-bold">Exchange Connections</h2>
            <p className="text-gray-300 text-sm mt-2">Link and manage your exchange accounts securely.</p>
          </div>

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Enhanced, Scrollable, Searchable and Accessible Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <label className="block text-gray-200 mb-2" htmlFor="exchange">
                Exchange
              </label>
              <button
                ref={buttonRef}
                type="button"
                onClick={() => {
                  setDropdownOpen(!dropdownOpen);
                  setFocusedIndex(-1);
                }}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <span className="flex items-center gap-2">
                  {exchanges.find((ex) => ex.name === selectedExchange) && (
                    <img 
                      src={exchanges.find((ex) => ex.name === selectedExchange).icon} 
                      alt={selectedExchange} 
                      className="w-5 h-5"
                    />
                  )}
                  {selectedExchange}
                </span>
                <ExpandMoreIcon fontSize="small" className={`transform transition ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              <p className="text-gray-300 text-sm mt-1">Choose the exchange you want to connect.</p>

              {dropdownOpen && (
                <div className="absolute mt-2 w-full bg-gray-700 rounded-lg shadow-lg py-2 z-20 animate-fadeIn max-h-48 overflow-y-auto focus:outline-none">
                  {/* Search Input */}
                  <div className="flex items-center px-3 py-2 bg-gray-600">
                    <SearchIcon fontSize="small" className="text-gray-300 mr-2" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setFocusedIndex(-1); // reset focus when searching
                      }}
                      className="w-full bg-gray-600 text-white placeholder-gray-400 outline-none"
                      placeholder="Search..."
                    />
                  </div>
                  {filteredExchanges.length === 0 && (
                    <div className="px-3 py-2 text-gray-400 italic">
                      No matches found.
                    </div>
                  )}
                  {filteredExchanges.map((ex, index) => {
                    const isSelected = selectedExchange === ex.name;
                    const isFocused = focusedIndex === index;
                    return (
                      <button
                        key={ex.name}
                        onClick={() => handleExchangeSelect(ex)}
                        onMouseEnter={() => setFocusedIndex(index)}
                        className={`flex items-center w-full px-3 py-2 text-left transition ${
                          isFocused ? 'bg-gray-600' : isSelected ? 'bg-gray-600' : 'hover:bg-gray-600'
                        }`}
                      >
                        <img src={ex.icon} alt={ex.name} className="w-5 h-5 mr-2" />
                        <span className="flex-grow">{ex.name}</span>
                        {isSelected && <CheckIcon fontSize="small" className="text-blue-400 ml-2" />}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div>
              <label className="block text-gray-200 mb-2" htmlFor="apiKey">
                API Key
              </label>
              <input
                type="text"
                id="apiKey"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your API Key"
              />
              <p className="text-gray-300 text-sm mt-1">Enter your API Key from the exchange.</p>
            </div>

            <div>
              <label className="block text-gray-200 mb-2" htmlFor="secretKey">
                Secret Key
              </label>
              <input
                type="password"
                id="secretKey"
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your Secret Key"
              />
              <p className="text-gray-300 text-sm mt-1">Enter your Secret Key from the exchange.</p>
            </div>
            
            <div> 
            <label className="block text-gray-200 mb-2" htmlFor="phrase">
              Secret Phrase
            </label>
            <input
              type="text"
              id="phrase"
              value={phrase}
              onChange={(e) => setPhrase(e.target.value)}
              className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" 
              placeholder="Enter your Phrase"
            />
            <p className="text-gray-300 text-sm mt-1">Enter your security phrase from the exchange.</p>
          </div>

          </div>

          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between mt-10">
            <div className="flex items-center text-sm space-x-2">
              {connectionStatus === 'success' && (
                <span className="flex items-center text-green-400 font-medium">
                  <CheckCircleOutlineIcon fontSize="small" className="mr-1" />
                  Connection successful!
                </span>
              )}
              {connectionStatus === 'error' && (
                <span className="flex items-center text-red-400 font-medium">
                  <ErrorOutlineIcon fontSize="small" className="mr-1" />
                  Failed to connect. Check your keys.
                </span>
              )}
            </div>
            
            <div className="flex space-x-4 mt-4 md:mt-0">
              <button
                onClick={testConnection}
                className="flex items-center space-x-2 border border-blue-500 text-blue-500 px-4 py-2 rounded-lg font-medium hover:bg-blue-500 hover:bg-opacity-20 transition-transform transform hover:-translate-y-0.5"
              >
                <RefreshIcon fontSize="small" />
                <span>Test Connection</span>
              </button>
              <button
                onClick={saveConnection}
                className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg font-semibold transition-transform transform hover:-translate-y-0.5"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      {/* BOT Section */}
      <div className="mt-5 bg-gray-800 rounded-lg p-8 relative overflow-hidden">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {[
          { name: "BTC_USDT", img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScGBnEyeJokV07T20QtlOYBLToFxNmbwxBbA&s" },
          { name: "ETH_USDT", img: "https://img.freepik.com/premium-photo/ethereum-logo-with-bright-glowing-futuristic-blue-lights-black-background_989822-5692.jpg" },
          { name: "BNB_USDT", img: "https://img.freepik.com/premium-psd/3d-icon-black-coin-with-golden-bnb-logo-center_930095-56.jpg" },
          { name: "SOL_USDT", img: "https://thumbs.dreamstime.com/b/solana-logo-coin-icon-isolated-cryptocurrency-token-vector-sol-blockchain-crypto-bank-254180447.jpg" },
          { name: "PEPE_USDT", img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToNJ9OKQv_DIjonr1s_TFrZbqN9hFjsD86eA&s" },
        ].map((bot, index) => (
          <div key={index} className="flex flex-col items-center">
            <img src={bot.img} alt={bot.name} className="w-full h-auto rounded-lg" />
            <button
              onClick={() => handleButtonClick(bot.name)}
              className={`mt-2 ${subscriptions[bot.name] ? "bg-red-500 hover:bg-red-600" : "bg-blue-500 hover:bg-blue-600"} text-white font-bold py-2 px-4 rounded-lg`}
            >
              {subscriptions[bot.name] ? "Unsubscribe" : "Subscribe"}
            </button>
          </div>
        ))}
      </div>

      {/* Subscribe Modal */}
      {isBotModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg max-w-md w-full">
            <h2 className="text-2xl font-bold text-white mb-4">Subscribe to {selectedBot}</h2>
            <p className="text-gray-300 text-sm mb-4">Enter the amount you'd like to use for this bot.</p>

            <input
              type="number"
              value={balance}
              onChange={(e) => setBalance(e.target.value)}
              className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter balance"
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSubscribe}
                className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Unsubscribe Modal */}
      {isUnsubscribeModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg max-w-md w-full">
            <h2 className="text-2xl font-bold text-white mb-4">Confirm Unsubscription</h2>
            <p className="text-gray-300 text-sm mb-4">
              Are you sure you want to unsubscribe from {selectedBot}?
            </p>

            <div className="flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleUnsubscribe}
                className="bg-red-500 hover:bg-red-600 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
      </div>
      <div className="flex-none">
        <Footer />
      </div>

    </div>
  );
}

export default ProfilePage;
