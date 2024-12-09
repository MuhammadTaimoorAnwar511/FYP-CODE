import React, { useEffect } from 'react';

const CoinList = () => {
    useEffect(() => {
        // Dynamically add the CoinGecko widget script to the page
        const script = document.createElement('script');
        script.src = 'https://widgets.coingecko.com/gecko-coin-list-widget.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script); // Clean up the script on component unmount
        };
    }, []);

    return (
        <div className="w-full h-full">
            {/* CoinGecko Coin List Widget */}
            <gecko-coin-list-widget 
                locale="en" 
                dark-mode="true" 
                outlined="true" 
                coin-ids="bitcoin,ethereum,binancecoin,solana,pepe" 
                initial-currency="usd"
            ></gecko-coin-list-widget>
        </div>
    );
};

export default CoinList;
