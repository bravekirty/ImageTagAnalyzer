// src/components/Analytics.jsx
import React, { useEffect, useState } from 'react';
import { getAnalytics } from '../services/api';

const Analytics = ({ analytics, onAnalytics, isLoading }) => {
    const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setIsLoadingAnalytics(true);
        try {
            const response = await getAnalytics();
            onAnalytics(response.data);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        } finally {
            setIsLoadingAnalytics(false);
        }
    };

    const getBubbleSize = (percentage) => {
        if (percentage > 70) return 'w-20 h-20 text-lg';
        if (percentage > 50) return 'w-16 h-16 text-base';
        if (percentage > 30) return 'w-14 h-14 text-sm';
        if (percentage > 15) return 'w-12 h-12 text-xs';
        return 'w-10 h-10 text-xs';
    };

    const getBubbleColor = (index) => {
        const colors = [
            'bg-gradient-to-br from-purple-500 to-pink-500',
            'bg-gradient-to-br from-blue-500 to-cyan-500',
            'bg-gradient-to-br from-green-500 to-emerald-500',
            'bg-gradient-to-br from-orange-500 to-red-500',
            'bg-gradient-to-br from-indigo-500 to-purple-600'
        ];
        return colors[index % colors.length];
    };

    if (isLoadingAnalytics) {
        return (
            <div className="bg-white rounded-2xl shadow-xl p-6 h-96 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
                <button
                    onClick={loadAnalytics}
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all"
                >
                    🔄 Refresh
                </button>
            </div>

            {analytics ? (
                <div className="space-y-6">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-gradient-to-br from-blue-100 to-blue-50 p-4 rounded-xl border border-blue-200">
                            <div className="text-2xl font-bold text-blue-700">
                                {analytics.total_images}
                            </div>
                            <div className="text-sm text-blue-600 font-medium">Total Images</div>
                        </div>
                        <div className="bg-gradient-to-br from-green-100 to-green-50 p-4 rounded-xl border border-green-200">
                            <div className="text-2xl font-bold text-green-700">
                                {analytics.avg_tags_per_image?.toFixed(1) || '0.0'}
                            </div>
                            <div className="text-sm text-green-600 font-medium">Avg Tags/Image</div>
                        </div>
                    </div>

                    {/* Bubble Chart */}
                    {/*
                    {analytics.top_tags && analytics.top_tags.length > 0 && (
                        <div>
                            <h3 className="font-bold text-lg mb-4 text-gray-700">Top Tags Bubble Chart</h3>
                            <div className="flex flex-wrap gap-4 justify-center">
                                {analytics.top_tags.slice(0, 5).map((tag, index) => (
                                    <div
                                        key={index}
                                        className={`flex flex-col items-center justify-center ${getBubbleSize(tag.percentage_on_images)} ${getBubbleColor(index)} text-white rounded-full shadow-lg transform hover:scale-110 transition-transform duration-200`}
                                    >
                                        <span className="font-bold">{tag.tag_name}</span>
                                        <span className="text-xs opacity-90">{tag.percentage_on_images}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    */}

                    {/* Top Tags List */}
                    {analytics.top_tags && analytics.top_tags.length > 0 && (
                        <div>
                            <h3 className="font-bold text-lg mb-3 text-gray-700">Top Tags Ranking</h3>
                            <div className="space-y-2">
                                {analytics.top_tags.map((tag, index) => (
                                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                        <div className="flex items-center space-x-3">
                                            <div className={`w-3 h-3 rounded-full ${getBubbleColor(index)}`}></div>
                                            <span className="font-medium">{tag.tag_name}</span>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-sm font-bold text-gray-700">{tag.percentage_on_images}% of images</div>
                                            <div className="text-xs text-gray-500">Avg confidence: {tag.avg_confidence}%</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">📊</div>
                    <p className="text-gray-500 text-lg">Analytics data will appear here</p>
                    <p className="text-sm text-gray-400 mt-2">Upload some images to see statistics</p>
                </div>
            )}
        </div>
    );
};

export default Analytics;