import React from 'react';
import Navbar2 from '../Components/Footer&Navbar/Navbar2';
import CoinHeatmap from '../Components/MarketOverview/CoinHeatmap';
import CoinTicker from '../Components/MarketOverview/CoinTicker';
import CoinList from '../Components/MarketOverview/CoinList';
import CoinPriceMarquee from '../Components/MarketOverview/CoinPriceMarquee';
import BTCCoinConverter from '../Components/MarketOverview/BTCCoinConverter';
import ETHCoinConverter from '../Components/MarketOverview/ETHCoinConverter';
import BNBCoinConverter from '../Components/MarketOverview/BNBCoinConverter';
import SOLCoinConverter from '../Components/MarketOverview/SOLCoinConverter';
import PEPECoinConverter from '../Components/MarketOverview/PEPECoinConverter';
import Footer from '../Components/Footer&Navbar/Footer';

const MarketOverview = () => {
    return (
        <div className="bg-black min-h-screen flex flex-col">
            {/* Navbar at the top */}
            <div className="flex-none">
                <Navbar2 />
            </div>

            {/* Price Marquee */}
            <div className="flex-none">
                <CoinPriceMarquee />
            </div>

            {/* Content Section */}
            <div className="flex-grow grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
                {/* Left Column */}
                <div className="flex flex-col gap-6">
                    {/* Heatmap */}
                    <div className="bg-black text-white">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-blue-500 to-blue-700 py-2 rounded-lg">
                            Coin Heatmap
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinHeatmap />
                        </div>
                    </div>

                    {/* Coin Ticker */}
                    <div className="bg-black text-white">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-green-500 to-green-700 py-2 rounded-lg">
                            Coin Ticker
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinTicker />
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div className="flex flex-col gap-6">
                    {/* Coin List */}
                    <div className="bg-black text-white">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-purple-500 to-purple-700 py-2 rounded-lg">
                            Coin List
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinList />
                        </div>
                    </div>

                    {/* Currency Converters */}
                    <div className="bg-black text-white">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-orange-500 to-orange-700 py-2 rounded-lg">
                            Currency Converters
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex items-center justify-center">
                                <BTCCoinConverter />
                            </div>
                            <div className="flex items-center justify-center">
                                <PEPECoinConverter />
                            </div>
                            <div className="flex items-center justify-center">
                                <ETHCoinConverter />
                            </div>
                            <div className="flex items-center justify-center">
                                <BNBCoinConverter />
                            </div>
                            <div className="flex items-center justify-center">
                                <SOLCoinConverter />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer at the bottom */}
            <div className="flex-none">
                <Footer />
            </div>
        </div>
    );
};

export default MarketOverview;