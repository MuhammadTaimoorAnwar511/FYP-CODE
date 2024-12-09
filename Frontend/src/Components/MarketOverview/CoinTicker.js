import React, { useEffect } from 'react';

const CoinTicker = () => {
    useEffect(() => {
        // Dynamically add the CoinGecko widget script to the page
        const script = document.createElement('script');
        script.src = 'https://widgets.coingecko.com/gecko-coin-ticker-widget.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script); // Clean up the script on component unmount
        };
    }, []);

    return (
        <div className="w-full h-full">
            {/* CoinGecko Ticker Widget */}
            <gecko-coin-ticker-widget 
                locale="en" 
                dark-mode="true" 
                outlined="true" 
                initial-currency="usd"
            ></gecko-coin-ticker-widget>
        </div>
    );
};

export default CoinTicker;
