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
import TopStories from '../Components/MarketOverview/top-stories';
import FearGreed from '../Components/MarketOverview/FearGreed';
import TechnicalAnalysis from '../Components/MarketOverview/TechnicalAnalysis';
import LatestNews from '../Components/MarketOverview/LatestNews';
import TredingNews from '../Components/MarketOverview/TredingNews';
import Screener from '../Components/MarketOverview/Screener';

const MarketOverview = () => {
    return (
        <div className="bg-black min-h-screen flex flex-col">
            {/* Navbar */}
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
                    {/* Coin Heatmap */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-cyan-500 to-teal-600 text-white py-2 rounded-lg shadow-md">
                            Coin Heatmap
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinHeatmap />
                        </div>
                    </div>

                    {/* Coin Ticker */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-emerald-500 to-green-600 text-white py-2 rounded-lg shadow-md">
                            Coin Ticker
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinTicker />
                        </div>
                    </div>
                        
                    {/* Screener */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700 flex flex-col">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-rose-500 to-red-600 text-white py-2 rounded-lg shadow-md">
                            Screener
                        </h2>
                        <div className="w-full h-full">
                            <Screener />
                        </div>
                    </div>
                    
                    {/* Fear and Greed + Technical Analysis */}
                    <div className="flex flex-col lg:flex-row justify-between gap-4">
                        {/* Fear and Greed Widget */}
                        <div className="flex-grow bg-black text-white p-4 rounded-lg border border-gray-700">
                            {/* Row 1: Crypto Fear and Greed Index */}
                            <div className="mb-12"> {/* Increased margin for highlighted gap */}
                                <h2 className="text-center text-xl font-bold bg-gradient-to-r from-red-500 to-rose-600 text-white py-2 rounded-lg shadow-md">
                                    Crypto Fear and Greed Index
                                </h2>
                                <div className="flex items-center justify-center w-full h-auto">
                                    <FearGreed />
                                </div>
                            </div>

                            {/* Row 2: Twitter Sentiments */}
                            <div>
                                <h2 className="text-center text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-2 rounded-lg shadow-md">
                                    Twitter Sentiments
                                </h2>
                                <div className="flex items-center justify-center w-full h-auto">
                                    <FearGreed />
                                </div>
                            </div>
                        </div>
                        {/* Technical Analysis Widget */}
                        <div className="flex-grow bg-black text-white p-4 rounded-lg border border-gray-700">
                            <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-blue-500 to-sky-600 text-white py-2 rounded-lg shadow-md">
                                Technical Analysis
                            </h2>
                            <div className="flex items-center justify-center w-full h-auto">
                                <TechnicalAnalysis symbol="BINANCE:BTCUSD" interval="1h" height="400" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column */}
                <div className="flex flex-col gap-6">
                    {/* Coin List */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-purple-500 to-violet-600 text-white py-2 rounded-lg shadow-md">
                            Coin List
                        </h2>
                        <div className="flex items-center justify-center">
                            <CoinList />
                        </div>
                    </div>

                    {/* Currency Converters */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-orange-500 to-yellow-600 text-white py-2 rounded-lg shadow-md">
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

                    {/* Top Stories */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700 flex flex-col">
                        <h2 className="text-center text-xl font-bold mb-4 bg-gradient-to-r from-pink-500 to-fuchsia-600 text-white py-2 rounded-lg shadow-md">
                            Market Top Stories
                        </h2>
                        <div className="w-full h-full">
                            <TopStories />
                        </div>
                    </div>

                    {/* Latest News and Trending News */}
                    <div className="bg-black text-white p-4 rounded-lg border border-gray-700 flex flex-row">
                        {/* Column 1: Latest News */}
                        <div className="w-1/2 pr-2">
                            <LatestNews />
                        </div>
                        {/* Column 2: Trending News */}
                        <div className="w-1/2 pl-2">
                            <TredingNews />
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="flex-none">
                <Footer />
            </div>
        </div>
    );
};

export default MarketOverview;
