import React, { useEffect } from 'react';

const TredingNews = () => {
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
                data-news_feed="trending" 
                data-bg_color="#070707FC" 
                data-text_color="#FFFFFF" 
                data-link_color="#0091C2" 
                data-header_bg_color="#1E7EA3" 
                data-header_text_color="#FFFFFF" 
                data-posts_limit="5" 
                className="CryptoPanicWidget"
                rel="noopener noreferrer"
            >
                Trending News
            </a>
        </div>
    );
};

export default TredingNews;
