import React from "react";
import Navbar from '../Components/Navbar'; 
import TradingViewWidget from "../Components/Charts/TradingViewWidget";

const Chart = () => {
  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Navbar */}
      <div className="flex-none">
        <Navbar />
      </div>
      
      {/* Content */}
      <div className="flex-grow flex items-center justify-center">
        <div className="w-full h-full">
          <TradingViewWidget />
        </div>
      </div>
    </div>
  );
};

export default Chart;
