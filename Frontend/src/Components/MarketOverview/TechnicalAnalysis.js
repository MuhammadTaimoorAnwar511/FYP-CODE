import React, { useEffect, useRef } from 'react';

const TechnicalAnalysis = ({ symbol = "BINANCE:BTCUSD", interval = "1m", width = "125", height = "150" }) => {
    const widgetRef = useRef(null);

    useEffect(() => {
        if (!widgetRef.current) return;

        const script = document.createElement('script');
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js";
        script.async = true;

        // Widget configuration
        script.innerHTML = JSON.stringify({
            interval,
            width: "100%", 
            height,
            symbol,
            showIntervalTabs: true,
            displayMode: "single",
            locale: "en",
            colorTheme: "dark",
            isTransparent: false,
        });

        // Clear existing widget content and append the new script
        widgetRef.current.innerHTML = '';
        widgetRef.current.appendChild(script);
    }, [symbol, interval, width, height]);

    return (
        <div className="tradingview-widget-container bg-black p-4 rounded-lg border border-gray-700">
            <div ref={widgetRef} className="tradingview-widget-container__widget"></div>
            <div className="text-center text-gray-400 text-sm mt-2">
                <a
                    href="https://www.tradingview.com/"
                    rel="noopener nofollow"
                    target="_blank"
                    className="text-blue-400 hover:underline"
                >
                    Track all markets on TradingView
                </a>
            </div>
        </div>
    );
};

export default TechnicalAnalysis;
