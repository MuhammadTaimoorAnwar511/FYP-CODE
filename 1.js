import React, { useState, useEffect } from "react";

const BotSubscription = ({ userData }) => {
  const [subscriptions, setSubscriptions] = useState({});
  const [isBotModalOpen, setIsBotModalOpen] = useState(false);
  const [isUnsubscribeModalOpen, setIsUnsubscribeModalOpen] = useState(false);
  const [selectedBot, setSelectedBot] = useState("");
  const [balance, setBalance] = useState("");

  const checkSubscriptionStatus = async (botName) => {
    const response = await fetch("http://localhost:5000/subscription/status", {
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
    const response = await fetch("http://localhost:5000/subscription/create", {
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
    if (data.message) {
      setSubscriptions(prev => ({ ...prev, [selectedBot]: true }));
      alert(data.message);
    }
    closeModal();
  };

  const handleUnsubscribe = async () => {
    const response = await fetch("http://localhost:5000/subscription/delete", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userData?._id,
        bot_name: selectedBot,
      }),
    });

    const data = await response.json();
    if (data.message) {
      setSubscriptions(prev => ({ ...prev, [selectedBot]: false }));
      alert(data.message);
    }
    closeModal();
  };

  return (
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
  );
};

export default BotSubscription;