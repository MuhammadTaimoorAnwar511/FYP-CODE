import React, { useEffect } from 'react';

const LatestNews = () => {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = "https://static.cryptopanic.com/static/js/widgets.min.js";
        script.async = true;
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <div className="crypto-panic-widget-container" style={{ width: '100%', height: 'auto', overflow: 'hidden' }}>
            <a 
                href="https://cryptopanic.com/" 
                target="_blank" 
                data-news_feed="recent" 
                data-bg_color="#070707FC" 
                data-font_family="sans" 
                data-header_bg_color="#4B2FE4" 
                data-header_text_color="#FFFFFF" 
                data-link_color="#0091C2" 
                data-posts_limit="5" 
                data-text_color="#FFFFFF" 
                className="CryptoPanicWidget"
                rel="noopener noreferrer"
            >
                Latest News
            </a>
        </div>
    );
};

export default LatestNews;
