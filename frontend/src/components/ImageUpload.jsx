// src/components/ImageUpload.jsx
import React, { useRef, useState, useEffect } from 'react';
import { uploadImage, getSampleImages, analyzeSampleImage } from '../services/api';
import toast from 'react-hot-toast';
import FullScreenImage from './FullScreenImage';

const ImageUpload = ({ onUpload, onTags, onLoading, isLoading, uploadedImage }) => {
    const fileInputRef = useRef(null);
    const [isDragging, setIsDragging] = useState(false);
    const [sampleImages, setSampleImages] = useState([]);
    const [loadingSamples, setLoadingSamples] = useState(false);
    const [showFullScreen, setShowFullScreen] = useState(false);

    // Load sample images from backend on component mount
    useEffect(() => {
        const loadSampleImages = async () => {
            setLoadingSamples(true);
            try {
                const response = await getSampleImages();
                setSampleImages(response.data || []);
            } catch (error) {
                console.error('Failed to load sample images:', error);
                toast.error('Failed to load sample images');
                setSampleImages([]);
            } finally {
                setLoadingSamples(false);
            }
        };

        loadSampleImages();
    }, []);

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

            const response = await uploadImage(formData);

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

        try {
            const response = await analyzeSampleImage(sample.id);

            let imageUrl = sample.image_url;
            if (imageUrl && !imageUrl.startsWith('http')) {
                imageUrl = `http://${imageUrl}`;
            }

            onUpload(imageUrl);
            onTags(response.data.tags || []);

            toast.success(`Analyzed sample: ${sample.filename}`);
        } catch (error) {
            console.error('Sample image error:', error);
            toast.error('Failed to analyze sample image');
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
                Image Analytics
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

            {/* Upload/Preview Area - Side by side */}
            <div className="flex gap-6 mb-6">
                {/* Upload Area - 2/3 width (ALWAYS VISIBLE) */}
                <div className="flex-1"> {/* This will take 2/3 space */}
                    <div
                        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200 h-full flex flex-col justify-center ${isDragging
                            ? 'border-blue-400 bg-blue-50'
                            : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
                            } ${isLoading ? 'opacity-60' : ''}`}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onClick={() => !isLoading && fileInputRef.current?.click()}
                    >
                        <div className="space-y-3">
                            <div className="text-4xl">📸</div>
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
                </div>

                {/* Image Preview - 1/3 width (ONLY WHEN IMAGE EXISTS) */}
                {uploadedImage && (
                    <div className="w-1/3"> {/* This will take 1/3 space */}
                        <div className="bg-gray-50 rounded-lg p-4 h-full flex flex-col">
                            <h3 className="text-sm font-semibold text-gray-700 mb-2">Image Preview</h3>
                            <div
                                className="relative flex-1 group cursor-zoom-in"
                                onClick={() => setShowFullScreen(true)}
                            >
                                <img
                                    src={uploadedImage}
                                    alt="Uploaded preview"
                                    className="w-full h-full max-h-48 object-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow"
                                />
                                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg flex items-center justify-center">
                                    <span className="text-white text-sm bg-black bg-opacity-50 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                                        Click for full screen
                                    </span>
                                </div>
                            </div>
                            <p className="text-xs text-gray-500 mt-2 text-center">
                                Click image to view full size
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Sample Images - Full width below */}
            <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Try sample images:</h3>

                {loadingSamples ? (
                    <div className="text-center py-4">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                        <p className="text-sm text-gray-500 mt-2">Loading samples...</p>
                    </div>
                ) : sampleImages.length > 0 ? (
                    <div className="grid grid-cols-3 gap-3">
                        {sampleImages.map((sample) => (
                            <button
                                key={sample.id}
                                onClick={() => !isLoading && handleSampleImage(sample)}
                                disabled={isLoading}
                                className="flex flex-col items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                title={sample.filename}
                            >
                                <span className="text-3xl mb-1">
                                    {sample.filename?.includes('strawberry') ? '🍓' :
                                        sample.filename?.includes('urban') ? '🌆' :
                                            sample.filename?.includes('autumn') ? '🍂' : '📷'}
                                </span>
                                <span className="text-xs text-gray-600 text-center leading-tight">
                                    {sample.filename?.split('.')[0]?.substring(0, 10)}
                                </span>
                            </button>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-gray-500 text-center py-4">
                        No sample images available
                    </p>
                )}
            </div>

            {/* Full Screen Image Viewer */}
            {showFullScreen && uploadedImage && (
                <FullScreenImage
                    imageUrl={uploadedImage}
                    altText="Uploaded preview"
                    onClose={() => setShowFullScreen(false)}
                />
            )}
        </div>
    );
};

export default ImageUpload;