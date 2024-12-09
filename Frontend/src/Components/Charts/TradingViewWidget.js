import React, { useEffect, useRef, memo } from 'react';

const TradingViewWidget = ({ symbol = "BINANCE:BTCUSDT", interval = "D", theme = "dark", autosize = true }) => {
  const container = useRef();

  useEffect(() => {
    if (!container.current) return;

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.onload = () => console.log("TradingView widget loaded successfully.");
    script.onerror = () => console.error("Error loading TradingView widget script.");
    script.innerHTML = JSON.stringify({
      autosize,
      symbol,
      interval,
      timezone: "Etc/UTC",
      theme,
      style: "1",
      locale: "en",
      withdateranges: true,
      hide_side_toolbar: false,
      allow_symbol_change: true,
      calendar: false,
    });

    container.current.innerHTML = ''; // Clear previous content
    container.current.appendChild(script);

    return () => {
      // Cleanup script to prevent multiple widget instances
      container.current.innerHTML = '';
    };
  }, [symbol, interval, theme, autosize]);

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: "100%", width: "100%" }}>
      <div className="tradingview-widget-container__widget" style={{ height: "100%", width: "100%" }}></div>
    </div>
  );
};

export default memo(TradingViewWidget);
