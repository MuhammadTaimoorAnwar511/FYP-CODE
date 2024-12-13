import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';

const FearGreed = () => {
    const [fearGreedData, setFearGreedData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('https://api.alternative.me/fng/?limit=1');
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                const data = await response.json();
                setFearGreedData(data.data[0]); // Get the latest data
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const getColorAndIcon = (classification) => {
        switch (classification) {
            case 'Extreme Fear':
                return { 
                    textColor: 'text-red-600', 
                    bgColor: 'bg-red-900/30', 
                    icon: <TrendingDown className="text-red-500" size={24} />,
                    borderColor: 'border-red-800'
                };
            case 'Fear':
                return { 
                    textColor: 'text-red-400', 
                    bgColor: 'bg-red-800/20', 
                    icon: <TrendingDown className="text-red-400" size={24} />,
                    borderColor: 'border-red-700'
                };
            case 'Neutral':
                return { 
                    textColor: 'text-yellow-400', 
                    bgColor: 'bg-yellow-800/20', 
                    icon: <Clock className="text-yellow-400" size={24} />,
                    borderColor: 'border-yellow-700'
                };
            case 'Greed':
                return { 
                    textColor: 'text-green-400', 
                    bgColor: 'bg-green-800/20', 
                    icon: <TrendingUp className="text-green-400" size={24} />,
                    borderColor: 'border-green-700'
                };
            case 'Extreme Greed':
                return { 
                    textColor: 'text-green-600', 
                    bgColor: 'bg-green-900/30', 
                    icon: <TrendingUp className="text-green-500" size={24} />,
                    borderColor: 'border-green-800'
                };
            default:
                return { 
                    textColor: 'text-gray-400', 
                    bgColor: 'bg-gray-800/20', 
                    icon: <Clock className="text-gray-400" size={24} />,
                    borderColor: 'border-gray-700'
                };
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[200px] text-white text-lg animate-pulse">
                Loading Fear & Greed Index...
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[200px] text-red-500 text-lg">
                Error fetching data: {error}
            </div>
        );
    }

    const { value, value_classification, timestamp } = fearGreedData;
    const date = new Date(timestamp * 1000).toLocaleDateString();
    const { textColor, bgColor, icon, borderColor } = getColorAndIcon(value_classification);

    return (
        <div className={`
            ${bgColor} 
            ${borderColor}
            border 
            rounded-xl 
            p-6 
            shadow-2xl 
            transform 
            transition-all 
            duration-300 
            hover:scale-105 
            hover:shadow-2xl 
            dark:bg-opacity-30
            max-w-xs 
            mx-auto
        `}>
            <div className="flex flex-col items-center justify-center space-y-4">
                <div className="flex items-center space-x-4">
                    {icon}
                    <div className={`
                        ${textColor} 
                        text-6xl 
                        font-bold 
                        tracking-tight 
                        animate-fade-in
                    `}>
                        {value}
                    </div>
                </div>
                <div className={`
                    ${textColor} 
                    text-2xl 
                    font-semibold 
                    tracking-wider 
                    uppercase
                `}>
                    {value_classification}
                </div>
                <div className="flex items-center space-x-2 text-gray-400 text-sm">
                    <Clock size={16} />
                    <span>Last Updated: {date}</span>
                </div>
            </div>
        </div>
    );
};

export default FearGreed;