import React from "react";

const exchanges = [
  { name: "Binance", logo: "https://cryptologos.cc/logos/binance-coin-bnb-logo.svg?v=024", link: "https://www.binance.com" },
  { name: "OKX", logo: "https://upload.wikimedia.org/wikipedia/commons/0/0a/Logo-OKX.png", link: "https://www.okx.com" },
  { name: "Bybit", logo: "https://dtd31o1ybbmk8.cloudfront.net/photos/f288e559f90ef082d07edd02d8456f42/thumb.jpg", link: "https://www.bybit.com" },
];

const Exchanges = () => {
  return (
    <section id="exchanges" className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Supported Exchanges
        </h2>
        <div className="mt-10 flex justify-center space-x-6">
          {exchanges.map((exchange, index) => (
            <a
              key={index}
              href={exchange.link}
              target="_blank"
              rel="noopener noreferrer"
              className="w-40 h-40 flex flex-col items-center justify-center bg-gray-800 rounded-lg shadow-md transform hover:scale-110 transition-transform duration-300"
            >
              <img
                src={exchange.logo}
                alt={exchange.name}
                className="w-16 h-16 mb-4 object-contain"
              />
              <h3 className="text-lg font-semibold">{exchange.name}</h3>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Exchanges;
