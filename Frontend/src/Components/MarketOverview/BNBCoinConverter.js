import React, { useEffect } from 'react';

const BNBCoinConverter = () => {
    useEffect(() => {
        // Dynamically add the CoinGecko widget script to the page
        const script = document.createElement('script');
        script.src = 'https://widgets.coingecko.com/gecko-coin-converter-widget.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script); // Clean up the script on component unmount
        };
    }, []);

    return (
        <div className="w-full h-full">
            {/* CoinGecko Coin Converter Widget */}
            <gecko-coin-converter-widget 
                locale="en" 
                dark-mode="true" 
                outlined="true" 
                coin-id="binancecoin" 
                initial-currency="usd"
            ></gecko-coin-converter-widget>
        </div>
    );
};

export default BNBCoinConverter;
