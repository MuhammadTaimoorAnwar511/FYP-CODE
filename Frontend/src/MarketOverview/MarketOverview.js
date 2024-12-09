import React from 'react';
import Navbar from '../Components/Navbar'; 
import CoinHeatmap from '../Components/MarketOverview/CoinHeatmap'; 
import CoinTicker from '../Components/MarketOverview/CoinTicker'; 
import CoinList from '../Components/MarketOverview/CoinList';
import CoinPriceMarquee from '../Components/MarketOverview/CoinPriceMarquee';
import BTCCoinConverter from '../Components/MarketOverview/BTCCoinConverter';
import ETHCoinConverter from '../Components/MarketOverview/ETHCoinConverter';
import BNBCoinConverter from '../Components/MarketOverview/BNBCoinConverter'
import SOLCoinConverter from '../Components/MarketOverview/SOLCoinConverter'
import PEPECoinConverter from '../Components/MarketOverview/PEPECoinConverter'

const MarketOverview = () => {
    return (
        <div className="bg-black min-h-screen">
            {/* Navbar at the top */}
            <Navbar />
            
            {/* Price Marquee */}
            <CoinPriceMarquee />

            {/* 2x2 Grid Layout */}
            <div className="min-h-screen grid grid-cols-1 md:grid-cols-2 gap-0 p-2">
                <div className="bg-black text-white flex items-center justify-center p-0">
                    <CoinHeatmap />
                </div>
                <div className="bg-black text-white grid grid-rows-2 gap-0 p-4">
                    {/* Row 1 */}
                    <div className="flex items-center justify-center p-2">
                        <CoinTicker />
                    </div>
                    {/* Row 2 */}
                    <div className="flex items-center justify-center p-2">
                        <BTCCoinConverter />
                    </div>
                </div>
                <div className="bg-black text-white flex items-center justify-center p-4">
                    <CoinList />
                </div>
                <div className="bg-black text-white grid grid-cols-1 md:grid-cols-2 gap-2 p-2">
                    {/* Divided into 4 equal parts */}
                    <div className="bg-black flex items-center justify-center p-2">
                        <PEPECoinConverter />
                    </div>
                    <div className="bg-black flex items-center justify-center p-2">
                        <ETHCoinConverter />
                    </div>
                    <div className="bg-black flex items-center justify-center p-2">
                        <BNBCoinConverter />
                    </div>
                    <div className="bg-black flex items-center justify-center p-2">
                        <SOLCoinConverter />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketOverview;
