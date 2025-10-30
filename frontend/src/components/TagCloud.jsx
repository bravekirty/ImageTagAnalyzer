// src/components/TagCloud.jsx
import React from 'react';

const TagCloud = ({ tags }) => {
    const getTagColor = (confidence, isPrimary) => {
        if (isPrimary) return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white border-purple-600';
        if (confidence > 80) return 'bg-gradient-to-r from-green-500 to-emerald-500 text-white border-green-600';
        if (confidence > 60) return 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white border-blue-600';
        if (confidence > 40) return 'bg-gradient-to-r from-yellow-400 to-orange-400 text-gray-800 border-yellow-500';
        return 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-700 border-gray-400';
    };

    const getTagSize = (confidence) => {
        if (confidence > 80) return 'text-lg px-4 py-3 rounded-xl';
        if (confidence > 60) return 'text-base px-4 py-2.5 rounded-lg';
        if (confidence > 40) return 'text-sm px-3 py-2 rounded-md';
        return 'text-xs px-3 py-1.5 rounded';
    };

    const getTagCategory = (confidence, isPrimary) => {
        if (confidence > 80) return '✅ Very Sure';
        if (confidence > 60) return '👍 Sure';
        if (confidence > 40) return '🤔 Maybe';
        return '⚠️ Low Confidence';
    };

    return (
        <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Discovered Tags ({tags.length})
                </h2>
            </div>

            <div className="flex flex-wrap gap-3">
                {tags.map((tag, index) => (
                    <span
                        key={index}
                        className={`
              inline-flex items-center justify-center border-2 font-semibold
              transition-all duration-200 hover:scale-105 hover:shadow-md
              ${getTagColor(tag.confidence, tag.is_primary)}
              ${getTagSize(tag.confidence)}
            `}
                        title={`Confidence: ${tag.confidence.toFixed(1)}% - ${getTagCategory(tag.confidence, tag.is_primary)}`}
                    >
                        {tag.tag_name}
                        {tag.is_primary && ' ⭐'}
                    </span>
                ))}
            </div>

            {tags.length > 0 && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
                    <div className="flex items-center space-x-2 text-sm text-blue-800">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <p>
                            <strong>Confidence Guide:</strong> Primary (⭐) &gt; 60% | Very Sure &gt; 80% | Sure &gt; 60% | Maybe &gt; 40%
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TagCloud;