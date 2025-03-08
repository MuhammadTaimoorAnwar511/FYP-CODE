"use client"

import { useState, useRef, useEffect, createContext, useContext } from "react"
import {
  RefreshCwIcon as RefreshIcon,
  CircleCheckIcon as CheckCircleOutlineIcon,
  UnderlineIcon as ErrorOutlineIcon,
  ExpandIcon as ExpandMoreIcon,
  CheckIcon,
  SearchIcon,
  CheckCircleIcon,
  XCircleIcon,
  InfoIcon,
  XIcon,
  Trash2Icon,
} from "lucide-react"
import Navbar2 from "../Components/Footer&Navbar/Navbar2"
import Footer from "../Components/Footer&Navbar/Footer"

// Environment variables
const API_HOST = process.env.REACT_APP_API_HOST
const API_PORT = process.env.REACT_APP_API_PORT
const BASE_URL = `http://${API_HOST}:${API_PORT}`

// Notification Context
const NotificationContext = createContext(undefined)

const useNotification = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error("useNotification must be used within a NotificationProvider")
  }
  return context
}

const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])
  const [nextId, setNextId] = useState(1)

  const showNotification = (message, type) => {
    const id = nextId
    setNextId((prevId) => prevId + 1)

    setNotifications((prev) => [...prev, { id, message, type }])

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      dismissNotification(id)
    }, 5000)
  }

  const dismissNotification = (id) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id))
  }

  return (
    <NotificationContext.Provider value={{ notifications, showNotification, dismissNotification }}>
      {children}
    </NotificationContext.Provider>
  )
}

// Notification Toast Component
const NotificationToast = () => {
  const { notifications, dismissNotification } = useNotification()

  if (notifications.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {notifications.map((notification) => {
        const { id, message, type } = notification

        let bgColor = "bg-gray-800"
        let icon = <InfoIcon className="h-5 w-5 text-blue-400" />

        if (type === "success") {
          bgColor = "bg-gray-800 border-l-4 border-green-500"
          icon = <CheckCircleIcon className="h-5 w-5 text-green-500" />
        } else if (type === "error") {
          bgColor = "bg-gray-800 border-l-4 border-red-500"
          icon = <XCircleIcon className="h-5 w-5 text-red-500" />
        } else if (type === "info") {
          bgColor = "bg-gray-800 border-l-4 border-blue-500"
          icon = <InfoIcon className="h-5 w-5 text-blue-500" />
        }

        return (
          <div key={id} className={`${bgColor} text-white p-4 rounded-md shadow-lg flex items-start animate-slideIn`}>
            <div className="mr-3 mt-0.5">{icon}</div>
            <div className="flex-1">
              <p>{message}</p>
            </div>
            <button onClick={() => dismissNotification(id)} className="ml-4 text-gray-400 hover:text-white">
              <XIcon className="h-5 w-5" />
            </button>
          </div>
        )
      })}
    </div>
  )
}

// Bot statistics component
const BotStats = ({ botName }) => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${BASE_URL}/bot/detail?botname=${botName}`)
        if (!response.ok) throw new Error("Failed to fetch bot stats")
        const data = await response.json()
        setStats(data)
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [botName])

  if (loading) return <div className="mt-2 text-gray-400 text-sm">Loading stats...</div>
  if (error) return <div className="mt-2 text-red-400 text-sm">Error loading stats</div>

  return (
    <div className="w-full mt-4 p-3 bg-gray-700 rounded-lg">
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="text-blue-400">Total Trades:</div>
        <div className="text-right">{stats["Total Trades"]}</div>

        <div className="text-green-400">Win Rate:</div>
        <div className="text-right">{stats["Win Rate (%)"].toFixed(2)}%</div>

        <div className="text-green-400">Winning Trades:</div>
        <div className="text-right">{stats["Winning Trades"]}</div>

        <div className="text-green-400">Max Winning Streak:</div>
        <div className="text-right">{stats["Max Winning Streak"]}</div>

        <div className="text-red-400">Losing Trades:</div>
        <div className="text-right">{stats["Losing Trades"]}</div>

        <div className="text-red-400">Max Losing Streak:</div>
        <div className="text-right">{stats["Max Losing Streak"]}</div>
      </div>
    </div>
  )
}

// Exchange selector component
const ExchangeSelector = ({
  selectedExchange,
  setSelectedExchange,
  setApiKey,
  setApiSecret,
  setPhrase,
  setConnectionStatus,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [focusedIndex, setFocusedIndex] = useState(-1)
  const dropdownRef = useRef(null)
  const buttonRef = useRef(null)

  const exchanges = [
    {
      name: "OKX",
      icon: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSu0QUtkN8EjVWEgvIfiQ5G7Wq833qsFYzL8g&s",
    },
    {
      name: "Binance (Coming soon)",
      icon: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsKz71ieYKv2qQ_qixqjTeoGJ9rhFWu5q--A&s",
    },
    {
      name: "BYBIT (Coming soon)",
      icon: "https://play-lh.googleusercontent.com/SJxOSA2a2WY2RYQKv99kKCQVVqA5tmgw2VHn_YY0gL4riv7eDDjZ46X5_6Jge-Ur8uo",
    },
  ]

  // Filter exchanges based on search term
  const filteredExchanges = exchanges.filter((ex) => ex.name.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleExchangeSelect = (exchange) => {
    setSelectedExchange(exchange.name)
    setApiKey("")
    setApiSecret("")
    setPhrase("")
    setConnectionStatus(null)
    setDropdownOpen(false)
    setFocusedIndex(-1)
  }

  // Close dropdown when clicked outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownOpen &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !buttonRef.current.contains(event.target)
      ) {
        setDropdownOpen(false)
        setFocusedIndex(-1)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [dropdownOpen])

  // Keyboard navigation
  const handleKeyDown = (e) => {
    if (!dropdownOpen) return

    const maxIndex = filteredExchanges.length - 1

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setFocusedIndex((prev) => (prev < maxIndex ? prev + 1 : 0))
        break
      case "ArrowUp":
        e.preventDefault()
        setFocusedIndex((prev) => (prev > 0 ? prev - 1 : maxIndex))
        break
      case "Enter":
        e.preventDefault()
        if (focusedIndex >= 0 && filteredExchanges[focusedIndex]) {
          handleExchangeSelect(filteredExchanges[focusedIndex])
        }
        break
      case "Escape":
        e.preventDefault()
        setDropdownOpen(false)
        setFocusedIndex(-1)
        break
      default:
        break
    }
  }

  useEffect(() => {
    if (dropdownOpen) {
      document.addEventListener("keydown", handleKeyDown)
    } else {
      document.removeEventListener("keydown", handleKeyDown)
    }
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [dropdownOpen, focusedIndex, filteredExchanges])

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-gray-200 mb-2" htmlFor="exchange">
        Exchange
      </label>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => {
          setDropdownOpen(!dropdownOpen)
          setFocusedIndex(-1)
        }}
        className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <span className="flex items-center gap-2">
          {exchanges.find((ex) => ex.name === selectedExchange) && (
            <img
              src={exchanges.find((ex) => ex.name === selectedExchange).icon || "/placeholder.svg"}
              alt={selectedExchange}
              className="w-5 h-5"
            />
          )}
          {selectedExchange}
        </span>
        <ExpandMoreIcon className={`transform transition ${dropdownOpen ? "rotate-180" : ""}`} />
      </button>
      <p className="text-gray-300 text-sm mt-1">Choose the exchange you want to connect.</p>

      {dropdownOpen && (
        <div className="absolute mt-2 w-full bg-gray-700 rounded-lg shadow-lg py-2 z-20 animate-fadeIn max-h-48 overflow-y-auto focus:outline-none">
          {/* Search Input */}
          <div className="flex items-center px-3 py-2 bg-gray-600">
            <SearchIcon className="text-gray-300 mr-2 h-4 w-4" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setFocusedIndex(-1) // reset focus when searching
              }}
              className="w-full bg-gray-600 text-white placeholder-gray-400 outline-none"
              placeholder="Search..."
            />
          </div>
          {filteredExchanges.length === 0 && <div className="px-3 py-2 text-gray-400 italic">No matches found.</div>}
          {filteredExchanges.map((ex, index) => {
            const isSelected = selectedExchange === ex.name
            const isFocused = focusedIndex === index
            return (
              <button
                key={ex.name}
                onClick={() => handleExchangeSelect(ex)}
                onMouseEnter={() => setFocusedIndex(index)}
                className={`flex items-center w-full px-3 py-2 text-left transition ${
                  isFocused ? "bg-gray-600" : isSelected ? "bg-gray-600" : "hover:bg-gray-600"
                }`}
              >
                <img src={ex.icon || "/placeholder.svg"} alt={ex.name} className="w-5 h-5 mr-2" />
                <span className="flex-grow">{ex.name}</span>
                {isSelected && <CheckIcon className="text-blue-400 ml-2 h-4 w-4" />}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Profile information component
const ProfileInfo = ({ userData, loading, error }) => {
  if (loading) {
    return (
      <div className="space-y-2">
        <div className="h-8 bg-gray-700 rounded animate-pulse w-48"></div>
        <div className="h-4 bg-gray-700 rounded animate-pulse w-64"></div>
        <div className="h-4 bg-gray-700 rounded animate-pulse w-32"></div>
      </div>
    )
  }

  if (error || !userData) {
    return (
      <div className="text-red-400">
        <ErrorOutlineIcon className="mr-2 h-5 w-5" />
        Error loading profile data
      </div>
    )
  }

  return (
    <>
      <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent animate-pulse-slow">
        {userData?.username}
      </h1>
      {userData?._id && <p className="text-gray-300 mt-1 text-sm">{userData._id}</p>}
      {userData?.email && <p className="text-gray-300 mt-1 text-sm">{userData.email}</p>}
      {userData?.country && <p className="text-gray-300 mt-1 text-sm">{userData.country}</p>}
      {userData?.Balance !== undefined && (<p className={`mt-1 text-sm font-semibold ${userData.Balance === 0 ? "text-red-500" : "text-green-400"}`}>Balance: ${userData.Balance}</p>)}
    </>
  )
}

// Bot subscription component
const BotSubscription = ({ userData, onSubscriptionUpdated }) => {
  const [subscriptions, setSubscriptions] = useState({})
  const [isBotModalOpen, setIsBotModalOpen] = useState(false)
  const [isUnsubscribeModalOpen, setIsUnsubscribeModalOpen] = useState(false)
  const [selectedBot, setSelectedBot] = useState("")
  const [balance, setBalance] = useState("100")
  const { showNotification } = useNotification()

  const bots = [
    {
      name: "BTC_USDT",
      img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScGBnEyeJokV07T20QtlOYBLToFxNmbwxBbA&s",
    },
    {
      name: "ETH_USDT",
      img: "https://img.freepik.com/premium-photo/ethereum-logo-with-bright-glowing-futuristic-blue-lights-black-background_989822-5692.jpg",
    },
    {
      name: "BNB_USDT",
      img: "https://img.freepik.com/premium-psd/3d-icon-black-coin-with-golden-bnb-logo-center_930095-56.jpg",
    },
    {
      name: "SOL_USDT",
      img: "https://thumbs.dreamstime.com/b/solana-logo-coin-icon-isolated-cryptocurrency-token-vector-sol-blockchain-crypto-bank-254180447.jpg",
    },
    {
      name: "1000PEPE_USDT",
      img: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToNJ9OKQv_DIjonr1s_TFrZbqN9hFjsD86eA&s",
    },
  ]

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
    })

    const data = await response.json()
    return data.subscribed
  }

  useEffect(() => {
    const fetchSubscriptions = async () => {
      const botNames = bots.map((bot) => bot.name)
      const subscriptionStatus = {}

      for (const botName of botNames) {
        const isSubscribed = await checkSubscriptionStatus(botName)
        subscriptionStatus[botName] = isSubscribed
      }

      setSubscriptions(subscriptionStatus)
    }

    if (userData?._id) {
      fetchSubscriptions()
    }
  }, [userData])

  const handleButtonClick = (botName) => {
    setSelectedBot(botName)
    if (subscriptions[botName]) {
      setIsUnsubscribeModalOpen(true)
    } else {
      setIsBotModalOpen(true)
    }
  }

  const closeModal = () => {
    setIsBotModalOpen(false)
    setIsUnsubscribeModalOpen(false)
    setSelectedBot("")
    setBalance("")
  }

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
    })

    const data = await response.json()

    if (data.error) {
      showNotification(data.error, "error")
    } else if (data.message) {
      setSubscriptions((prev) => ({ ...prev, [selectedBot]: true }))
      showNotification(data.message, "success")

      // Call the callback to refresh data
      if (onSubscriptionUpdated) {
        onSubscriptionUpdated()
      }
    }

    closeModal()
  }

  const handleUnsubscribe = async () => {
    if (!userData?._id || !selectedBot) {
      showNotification("User ID or bot name is missing!", "error")
      return
    }

    const response = await fetch(`${BASE_URL}/subscription/delete/${userData._id}/${selectedBot}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })

    const data = await response.json()

    if (data.message) {
      setSubscriptions((prev) => ({ ...prev, [selectedBot]: false }))
      showNotification(data.message, "success")

      // Call the callback to refresh data
      if (onSubscriptionUpdated) {
        onSubscriptionUpdated()
      }
    } else if (data.error) {
      showNotification(data.error, "error")
    }

    closeModal()
  }

  return (
    <div className="mt-5 bg-gray-800 rounded-lg p-8 relative overflow-hidden">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {bots.map((bot, index) => (
          <div key={index} className="flex flex-col items-center">
            <img src={bot.img || "/placeholder.svg"} alt={bot.name} className="w-full h-auto rounded-lg" />
            <BotStats botName={bot.name} />
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
              onChange={(e) => {
                let newValue = Number(e.target.value);

                // Ensure the value is at least 100 USDT
                if (newValue < 100) {
                  newValue = 100;
                }

                setBalance(newValue);
              }}
              min="100"  // Ensures the input UI also prevents values below 100
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
            <p className="text-gray-300 text-sm mb-4">Are you sure you want to unsubscribe from {selectedBot}?</p>

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
  )
}

// Exchange connection form component
const ExchangeConnectionForm = ({ userData, onConnectionUpdated }) => {
  const [selectedExchange, setSelectedExchange] = useState("OKX")
  const [apiKey, setApiKey] = useState("")
  const [apiSecret, setApiSecret] = useState("")
  const [phrase, setPhrase] = useState("")
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const { showNotification } = useNotification()

  // Check if user has configured exchange credentials
  const hasExchangeCredentials = !!(userData?.exchange && userData?.api_key && userData?.secret_key)

  // Add useEffect to initialize form with user data if available
  useEffect(() => {
    if (userData?.exchange) {
      setSelectedExchange(userData.exchange)
    }
    if (userData?.api_key) {
      setApiKey(userData.api_key)
    }
    if (userData?.secret_key) {
      setApiSecret(userData.secret_key)
    }
    if (userData?.secret_phrase) {
      setPhrase(userData.secret_phrase)
    }
  }, [userData])

  const testConnection = async () => {
    if (!apiKey || !apiSecret || !phrase) {
      setConnectionStatus("error")
      showNotification("Please fill in all fields", "error")
      setTimeout(() => setConnectionStatus(null), 3000)
      return
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
      })

      const data = await response.json()

      if (data.success) {
        setConnectionStatus("success")
        showNotification("Connection successful!", "success")
      } else {
        setConnectionStatus("error")
        showNotification("Connection failed. Please check your credentials.", "error")
      }
    } catch (error) {
      console.error("Error testing connection:", error)
      setConnectionStatus("error")
      showNotification("Connection error. Please try again.", "error")
    }

    setTimeout(() => setConnectionStatus(null), 3000)
  }

  const saveConnection = async () => {
    const token = localStorage.getItem("access_token")

    try {
      const response = await fetch(`${BASE_URL}/exchange/SaveConnection`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          selectedExchange,
          apiKey,
          apiSecret,
          phrase,
        }),
      })

      const data = await response.json()
      if (response.ok) {
        showNotification("Exchange details updated successfully!", "success")
        // Call the callback to refresh user data
        if (onConnectionUpdated) {
          onConnectionUpdated()
        }
      } else {
        showNotification(`Error: ${data.message}`, "error")
      }
    } catch (error) {
      console.error("Error updating exchange details:", error)
      showNotification("Something went wrong!", "error")
    }
  }

  const deleteConnection = async () => {
    const token = localStorage.getItem("access_token");
  
    try {
      const response = await fetch(`${BASE_URL}/exchange/DeleteConnection`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
  
      const data = await response.json();
      if (response.ok) {
        // Clear form fields
        setApiKey("");
        setApiSecret("");
        setPhrase("");
        setSelectedExchange("OKX");
  
        showNotification("Exchange connection deleted successfully!", "success");
  
        // Call the callback to refresh user data
        if (onConnectionUpdated) {
          onConnectionUpdated();
        }
      } else {
        // Check if the user needs to unsubscribe from bots first
        if (data.subscribed_bots) {
          showNotification(
            `Error: You are subscribed to the following bots: ${data.subscribed_bots.join(
              ", "
            )}. Unsubscribe first.`,
            "error"
          );
        } else {
          showNotification(`Error: ${data.error}`, "error");
        }
      }
    } catch (error) {
      console.error("Error deleting exchange connection:", error);
      showNotification("Something went wrong!", "error");
    }
  
    setIsDeleteModalOpen(false);
  };
  

  return (
    <div className="bg-gray-800 rounded-lg p-8 mt-12 relative overflow-hidden min-h-[430px]">
      <div className="absolute inset-0 opacity-20 bg-gradient-to-br from-gray-700 to-gray-900"></div>
      <div className="relative z-10 border-b border-gray-700 pb-4 mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Exchange Connections</h2>
          <p className="text-gray-300 text-sm mt-2">Link and manage your exchange accounts securely.</p>
        </div>

        {/* Delete button - only visible if user has configured exchange credentials */}
        {hasExchangeCredentials && (
          <button
            onClick={() => setIsDeleteModalOpen(true)}
            className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-lg flex items-center gap-2 transition-transform transform hover:-translate-y-0.5"
          >
            <Trash2Icon className="h-4 w-4" />
            <span>Delete</span>
          </button>
        )}
      </div>

      <div className="relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6">
        <ExchangeSelector
          selectedExchange={selectedExchange}
          setSelectedExchange={setSelectedExchange}
          setApiKey={setApiKey}
          setApiSecret={setApiSecret}
          setPhrase={setPhrase}
          setConnectionStatus={setConnectionStatus}
        />

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
          {connectionStatus === "success" && (
            <span className="flex items-center text-green-400 font-medium">
              <CheckCircleOutlineIcon className="mr-1 h-5 w-5" />
              Connection successful!
            </span>
          )}
          {connectionStatus === "error" && (
            <span className="flex items-center text-red-400 font-medium">
              <ErrorOutlineIcon className="mr-1 h-5 w-5" />
              Failed to connect. Check your keys.
            </span>
          )}
        </div>

        <div className="flex space-x-4 mt-4 md:mt-0">
          <button
            onClick={testConnection}
            className="flex items-center space-x-2 border border-blue-500 text-blue-500 px-4 py-2 rounded-lg font-medium hover:bg-blue-500 hover:bg-opacity-20 transition-transform transform hover:-translate-y-0.5"
          >
            <RefreshIcon className="h-5 w-5" />
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

      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg max-w-md w-full">
            <h2 className="text-2xl font-bold text-white mb-4">Confirm Deletion</h2>
            <p className="text-gray-300 text-sm mb-4">
              Are you sure you want to delete your exchange connection? This will remove all your API keys and
              connection settings.
            </p>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setIsDeleteModalOpen(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={deleteConnection}
                className="bg-red-500 hover:bg-red-600 text-white font-medium px-4 py-2 rounded-lg transition"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Main profile page component
const ProfilePage = () => {
  const [userData, setUserData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Function to fetch user profile data
  const fetchProfile = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      if (!token) {
        throw new Error("No authentication token found")
      }
      const response = await fetch(`${BASE_URL}/user/profile`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch profile data")
      }

      const data = await response.json()
      setUserData(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Trigger refresh when refreshTrigger changes
  useEffect(() => {
    fetchProfile()
  }, [refreshTrigger])

  // Function to trigger a refresh
  const refreshData = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <NotificationProvider>
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
                  <ProfileInfo userData={userData} loading={loading} error={error} />
                </div>
              </div>
            </div>
          </div>

          {/* Exchange Connections Section */}
          <ExchangeConnectionForm userData={userData} onConnectionUpdated={refreshData} />

          {/* Bot Subscription Section */}
          <BotSubscription userData={userData} onSubscriptionUpdated={refreshData} />
        </div>
        <div className="flex-none">
          <Footer />
        </div>
        <NotificationToast />
      </div>
    </NotificationProvider>
  )
}

export default ProfilePage

