// src/App.jsx
import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import TagCloud from './components/TagCloud';
import Analytics from './components/Analytics';
import { Toaster } from 'react-hot-toast';

function App() {
    const [uploadedImage, setUploadedImage] = useState(null);
    const [tags, setTags] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <header className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-800 mb-4">
                        🎯 Image Tag Analyzer
                    </h1>
                    <p className="text-lg text-gray-600">
                        Upload images and discover what AI sees in them
                    </p>
                </header>

                {/* Main Content */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column - Upload & Results */}
                    <div className="space-y-8">
                        <ImageUpload
                            onUpload={setUploadedImage}
                            onTags={setTags}
                            onLoading={setIsLoading}
                            isLoading={isLoading}
                            uploadedImage={uploadedImage}
                        />

                        {/* Show tags only when we have them */}
                        {tags.length > 0 && (
                            <TagCloud tags={tags} />
                        )}
                    </div>

                    {/* Right Column - Analytics */}
                    <div className="space-y-8">
                        <Analytics
                            analytics={analytics}
                            onAnalytics={setAnalytics}
                            isLoading={isLoading}
                        />
                    </div>
                </div>
            </div>
            <Toaster position="top-right" />
        </div>
    );
}

export default App;