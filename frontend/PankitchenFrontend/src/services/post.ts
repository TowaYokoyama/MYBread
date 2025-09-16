import api from './api';
import { getAccessToken } from './auth';

export interface PhotoCreate {
  url: string;
  order: number;
}

export interface PostCreate {
  title: string;
  description: string; // content を description に変更
  bread_type: string; // bread_type を追加
  photos?: PhotoCreate[]; // photos プロパティを追加
}

export interface Photo {
  id: number;
  url: string;
  order: number;
  post_id: number;
}

export interface Post {
  id: number;
  title: string;
  description: string; // content を description に変更
  user_id: number;
  created_at: string;
  photos?: Photo[]; // photos プロパティを追加
  bread_type: string; // bread_type プロパティを追加
}

export const createPost = async (postData: PostCreate): Promise<Post> => {
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      throw new Error('No access token available');
    }
    const response = await api.post<Post>('/posts/', postData, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Create post failed:', error);
    throw error;
  }
};

export const getAllPosts = async (): Promise<Post[]> => {
  try {
    const response = await api.get<Post[]>('/posts/');
    return response.data;
  } catch (error) {
    console.error('Get all posts failed:', error);
    throw error;
  }
};

export const deletePost = async (postId: number): Promise<void> => {
  console.log('Calling deletePost for ID:', postId); // デバッグログを追加
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      throw new Error('No access token available');
    }
    await api.delete(`/posts/${postId}`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch (error) {
    console.error('Delete post failed:', error);
    throw error;
  }
};

export const uploadImage = async (imageUri: string, fileName: string): Promise<{ url: string }> => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: imageUri,
      name: fileName,
      type: 'image/jpeg', // または適切なMIMEタイプ
    } as any); // FormData.append の型定義が厳しいため any を使用

    const response = await api.post<{ url: string }>('/upload-image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Upload image failed:', error);
    throw error;
  }
};