import { API_BASE_URL } from '@/lib/api-config';
import { ApiResponse, GalleryItem } from '@/types/gallery';

export async function fetchRandomImages(offset: number = 0, limit: number = 20): Promise<GalleryItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}api/random-image?offset=${offset}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: ApiResponse = await response.json();

    if (!result.success || !result.data) {
      throw new Error('API request failed');
    }

    return result.data.map((item) => ({
      id: item.image_id,
      src: convertImagePath(item.image_path),
      category: item.category,
      description: item.description,
    }));
  } catch (error) {
    console.error('Error fetching images:', error);
    throw error;
  }
}

export async function searchImages(keyword: string, offset: number = 0, limit: number = 20): Promise<GalleryItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}api/search?keyword=${encodeURIComponent(keyword)}&offset=${offset}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: ApiResponse = await response.json();

    if (!result.success || !result.data) {
      throw new Error('API request failed');
    }

    return result.data.map((item) => ({
      id: item.image_id,
      src: convertImagePath(item.image_path),
      category: item.category,
      description: item.description,
    }));
  } catch (error) {
    console.error('Error searching images:', error);
    throw error;
  }
}

function convertImagePath(imagePath: string): string {
  const isDevelopment = process.env.NODE_ENV === 'development';

  if (isDevelopment) {
    return `http://127.0.0.1:5000/${imagePath.replace(/\\/g, '/')}`;
  }

  return `/${imagePath.replace(/\\/g, '/')}`;
}
