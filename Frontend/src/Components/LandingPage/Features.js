import React from "react";

const Features = () => {
  const features = [
    { title: "Technical Analysis", description: "Our bot uses LSTM models for advanced technical analysis on multiple timeframes.", icon: "📊" },
    { title: "Sentiment Analysis", description: "We employ BERT for accurate market sentiment analysis.", icon: "🧠" },
    { title: "Multi-Timeframe Strategy", description: "Our bot analyzes 1-hour, 4-hour, and 1-day timeframes for comprehensive market insights.", icon: "⏱️" },
  ];

  return (
    <section id="features" className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto text-center px-6">
        <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          How Our Bot Works
        </h2>
        <div className="mt-12 grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-800 shadow-lg rounded-lg p-6 text-center transform hover:scale-105 transition-transform duration-300"
            >
              <div className="text-4xl">{feature.icon}</div>
              <h3 className="text-xl font-semibold mt-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                {feature.title}
              </h3>
              <p className="text-gray-400 mt-2">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
