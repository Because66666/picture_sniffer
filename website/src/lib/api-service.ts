import { API_BASE_URL } from '@/lib/api-config';
import { ApiResponse, GalleryItem } from '@/types/gallery';

export interface LoginResponse {
  success: boolean;
  message?: string;
}

export async function login(token: string): Promise<LoginResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    const data: LoginResponse = await response.json();

    if (data.success) {
      localStorage.setItem('auth_token', token);
    }

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('auth_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

export async function fetchRandomImages(offset: number = 0, limit: number = 20): Promise<GalleryItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}api/random-image?offset=${offset}&limit=${limit}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
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
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
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

export async function describeImage(imageId: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}api/describe-image`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ image_id: imageId }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: { success: boolean; data: string } = await response.json();

    if (!result.success) {
      throw new Error('API request failed');
    }

    return result.data;
  } catch (error) {
    console.error('Error describing image:', error);
    throw error;
  }
}

export async function getImageById(imageId: string): Promise<GalleryItem> {
  try {
    const response = await fetch(`${API_BASE_URL}api/image/${imageId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: { success: boolean; data: any } = await response.json();

    if (!result.success || !result.data) {
      throw new Error('API request failed');
    }

    const imageData = result.data;
    return {
      id: imageData.image_id,
      src: convertImagePath(imageData.image_path),
      category: imageData.category,
      description: imageData.description,
    };
  } catch (error) {
    console.error('Error fetching image by id:', error);
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
