import React, { useEffect } from "react";

const PEPECoinConverter = () => {
  useEffect(() => {
    // Ensure the widget script is added to the DOM
    const scriptId = "gecko-coin-converter-widget-script";

    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.src = "https://widgets.coingecko.com/gecko-coin-converter-widget.js";
      script.type = "text/javascript";
      script.async = true;
      script.id = scriptId;

      document.body.appendChild(script);
    }
  }, []);

  return (
    <div className="pepe-coin-converter-widget w-full h-full">
      <gecko-coin-converter-widget
        locale="en"
        dark-mode="true"
        transparent-background="true"
        coin-id="pepe"
        initial-currency="usd"
      ></gecko-coin-converter-widget>
    </div>
  );
};

export default PEPECoinConverter;