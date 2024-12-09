import React, { useEffect } from 'react';

const CoinPriceMarquee = () => {
    useEffect(() => {
        // Dynamically add the CoinGecko widget script to the page
        const script = document.createElement('script');
        script.src = 'https://widgets.coingecko.com/gecko-coin-price-marquee-widget.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script); // Clean up the script on component unmount
        };
    }, []);

    return (
        <div className="w-full h-full">
            {/* CoinGecko Coin Price Marquee Widget */}
            <gecko-coin-price-marquee-widget 
                locale="en" 
                dark-mode="true" 
                outlined="true" 
                coin-ids="bitcoin,ethereum,binancecoin,solana,pepe" 
                initial-currency="usd"
            ></gecko-coin-price-marquee-widget>
        </div>
    );
};

export default CoinPriceMarquee;
