import React, { useEffect } from 'react';

const CoinHeatmap = () => {
    useEffect(() => {
        // Dynamically add the CoinGecko widget script to the page
        const script = document.createElement('script');
        script.src = 'https://widgets.coingecko.com/gecko-coin-heatmap-widget.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script); // Clean up the script on component unmount
        };
    }, []);

    return (
        <div className="w-full h-full">
            {/* CoinGecko Heatmap Widget */}
            <gecko-coin-heatmap-widget locale="en" dark-mode="true" outlined="true" top="25"></gecko-coin-heatmap-widget>
        </div>
    );
};

export default CoinHeatmap;
