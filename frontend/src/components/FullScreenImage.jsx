// src/components/FullScreenImage.jsx
import React from 'react';

const FullScreenImage = ({ imageUrl, altText = "Image", onClose }) => {
    if (!imageUrl) return null;

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-0 m-0 overflow-hidden"
            style={{ margin: 0 }}
            onClick={onClose}
        >
            <div className="relative w-full h-full flex items-center justify-center">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-white text-2xl bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70 transition-all z-10 border-0 focus:outline-none"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>

                </button>

                <div className="flex items-center justify-center w-full h-full p-4">
                    <img
                        src={imageUrl}
                        alt={altText}
                        className="max-w-full max-h-full object-contain"
                        onClick={(e) => e.stopPropagation()}
                    />
                </div>

                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-white text-sm bg-black bg-opacity-50 rounded px-3 py-1">
                    Click outside the image to close
                </div>
            </div>
        </div>
    );
};

export default FullScreenImage;