import React from "react";

const coinLogos = [
  { name: "BTC", logo: "https://cryptologos.cc/logos/bitcoin-btc-logo.svg?v=024" },
  { name: "ETH", logo: "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=024" },
  { name: "BNB", logo: "https://cryptologos.cc/logos/bnb-bnb-logo.svg?v=024" },
  { name: "SOL", logo: "https://cryptologos.cc/logos/solana-sol-logo.svg?v=024" },
  { name: "PEPE", logo: "https://cryptologos.cc/logos/pepe-pepe-logo.svg?v=024" },
];

const CoinLogos = () => {
  return (
    <section id="coins" className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto text-center px-6">
        <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Supported Coins
        </h2>
        <div className="mt-12 grid grid-cols-2 md:grid-cols-5 gap-8 justify-center items-center">
          {coinLogos.map((coin, index) => (
            <div
              key={index}
              className="flex flex-col items-center space-y-2 p-4 bg-gray-800 rounded-full shadow-lg transform hover:scale-105 transition-transform duration-300"
            >
              <img
                src={coin.logo}
                alt={coin.name}
                className="w-16 h-16 object-contain"
              />
              <span className="text-lg font-semibold">{coin.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CoinLogos;
