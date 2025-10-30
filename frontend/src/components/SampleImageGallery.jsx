// src/components/ImageUpload.jsx
import React, { useRef, useState } from 'react';
import { uploadImage } from '../services/api';
import toast from 'react-hot-toast';

const ImageUpload = ({ onUpload, onTags, onLoading, isLoading }) => {
    const fileInputRef = useRef(null);
    const [isDragging, setIsDragging] = useState(false);

    // Sample image data with pre-analyzed tags
    const sampleImages = [
        {
            id: 1,
            emoji: "🍓",
            name: "Ripe Strawberry",
            description: "A strawberry hangs from a slender green bough",
            imageUrl: "http://localhost:8000/static/samples/strawberry.jpg"
        },
        {
            id: 2,
            emoji: "🌆",
            name: "Modern Cityscape",
            description: "Modern city skyline with buildings and streets",
            imageUrl: "http://localhost:8000/static/samples/urban.jpg"
        },
        {
            id: 3,
            emoji: "🍂",
            name: "Autumn Forest",
            description: "A sun-dappled autumn forest with fiery foliage",
            imageUrl: "http://localhost:8000/static/samples/autumn.jpg"
        }
    ];

    const handleFileSelect = async (file) => {
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            toast.error('Please select an image file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            toast.error('Image size must be less than 10MB');
            return;
        }

        onLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            console.log('Sending to API...', file.name);

            const response = await uploadImage(formData);
            console.log('API Response:', response.data);

            // Create object URL for preview
            const imageUrl = URL.createObjectURL(file);
            onUpload(imageUrl);
            onTags(response.data.tags || []);

            toast.success('Image analyzed successfully!');
        } catch (error) {
            console.error('Upload error:', error);
            const errorMessage = error.response?.data?.detail ||
                error.response?.data?.message ||
                'Failed to analyze image';
            toast.error(errorMessage);
        } finally {
            onLoading(false);
        }
    };

    const handleSampleImage = async (sample) => {
        onLoading(true);

        // Simulate API delay for realism
        await new Promise(resolve => setTimeout(resolve, 1500));

        try {
            // Use the sample image URL and pre-analyzed tags
            onUpload(sample.imageUrl);
            onTags(sample.tags);

            toast.success(`Analyzed sample: ${sample.name}`);
        } catch (error) {
            toast.error('Failed to load sample image');
        } finally {
            onLoading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleInputChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-lg p-6 relative">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                Upload Image
            </h2>

            {/* Loading Overlay */}
            {isLoading && (
                <div className="absolute inset-0 bg-white bg-opacity-90 rounded-lg flex items-center justify-center z-10">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-3"></div>
                        <p className="text-blue-600 font-medium">Analyzing your image...</p>
                        <p className="text-sm text-blue-400">This may take a few seconds</p>
                    </div>
                </div>
            )}

            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${isDragging
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
                    } ${isLoading ? 'opacity-60' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => !isLoading && fileInputRef.current?.click()}
            >
                <div className="space-y-3">
                    <div className="text-6xl">📸</div>
                    <p className="text-gray-600">
                        {isDragging ? 'Drop image here' : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500">
                        PNG, JPG, GIF up to 10MB
                    </p>
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleInputChange}
                    disabled={isLoading}
                />
            </div>

            {/* Sample Images Grid */}
            <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Try sample images:</h3>
                <div className="grid grid-cols-3 gap-3">
                    {sampleImages.map((sample) => (
                        <button
                            key={sample.id}
                            onClick={() => !isLoading && handleSampleImage(sample)}
                            disabled={isLoading}
                            className="flex flex-col items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            title={sample.name}
                        >
                            <span className="text-3xl mb-1">{sample.emoji}</span>
                            <span className="text-xs text-gray-600 text-center leading-tight">
                                {sample.name.split(' ')[0]}
                            </span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ImageUpload;