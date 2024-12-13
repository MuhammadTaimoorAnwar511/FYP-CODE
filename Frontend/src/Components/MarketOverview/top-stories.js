import React, { useEffect } from 'react';

const TopStories = () => {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-timeline.js';
        script.async = true;
        script.innerHTML = JSON.stringify({
            feedMode: 'all_symbols',
            isTransparent: false,
            displayMode: 'adaptive',
            width: '100%',
            height: 400, 
            colorTheme: 'dark',
            locale: 'en',
        });

        const widgetContainer = document.getElementById('tradingview-widget');
        if (widgetContainer) {
            widgetContainer.appendChild(script);
        }

        return () => {
            if (widgetContainer) {
                widgetContainer.innerHTML = '';
            }
        };
    }, []);

    return (
        <div className="tradingview-widget-container" style={{ width: '100%', height: '400px' }}>
            <div id="tradingview-widget" className="tradingview-widget-container__widget"></div>
            <div className="tradingview-widget-copyright">
                <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
                    <span className="blue-text">Track all markets on TradingView</span>
                </a>
            </div>
        </div>
    );
};

export default TopStories;
