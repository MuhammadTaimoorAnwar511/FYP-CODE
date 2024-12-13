import React from "react";
import Navbar2 from '../Components/Footer&Navbar/Navbar2'; 
import TradingViewWidget from "../Components/Charts/TradingViewWidget";
import Footer from "../Components/Footer&Navbar/Footer";

const Chart = () => {
  return (
    <>
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Navbar */}
      <div className="flex-none">
        <Navbar2 />
      </div>
      
      {/* Content */}
      <div className="flex-grow flex items-center justify-center">
        <div className="w-full h-full">
          <TradingViewWidget />
        </div>
      </div>
    </div>
    {/* <Footer/> */}
    </>
  );
};

export default Chart;