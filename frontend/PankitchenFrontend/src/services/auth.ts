import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ACCESS_TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';

// トークンを保存
export const saveTokens = async (accessToken: string, refreshToken: string) => {
  await AsyncStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  await AsyncStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

// アクセストークンを取得
export const getAccessToken = async (): Promise<string | null> => {
  return await AsyncStorage.getItem(ACCESS_TOKEN_KEY);
};

// リフレッシュトークンを取得
export const getRefreshToken = async (): Promise<string | null> => {
  return await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
};

// トークンを削除（ログアウト時）
export const clearTokens = async () => {
  await AsyncStorage.removeItem(ACCESS_TOKEN_KEY);
  await AsyncStorage.removeItem(REFRESH_TOKEN_KEY);
};

// ログインAPI呼び出し
export const login = async (email: string, password: string) => {
  try {
    interface TokenResponse {
      access_token: string;
      refresh_token: string;
    }
    const response = await api.post<TokenResponse>('/token', `username=${email}&password=${password}`, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    const { access_token, refresh_token } = response.data;
    await saveTokens(access_token, refresh_token);
    return true;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

// ユーザー登録API呼び出し
export const register = async (email: string, password: string) => {
  try {
    const response = await api.post('/users/', { email, password });
    // 登録後、自動的にログインさせる場合はここでlogin関数を呼び出す
    // 今回は登録成功したらログイン画面に戻る想定
    return true;
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
};

// トークンリフレッシュAPI呼び出し
export const refreshAccessToken = async () => {
  try {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    interface TokenResponse {
      access_token: string;
      refresh_token: string;
    }
    const response = await api.post<TokenResponse>(`/token/refresh/?refresh_token=${refreshToken}`);
    const { access_token, refresh_token: new_refresh_token } = response.data;
    await saveTokens(access_token, new_refresh_token);
    return access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    await clearTokens(); // リフレッシュ失敗時はトークンをクリア
    throw error;
  }
};

// 認証済みユーザー情報を取得（保護されたエンドポイントの例）
export const getAuthenticatedUser = async () => {
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      throw new Error('No access token available');
    }
    const response = await api.get<User>('/users/me/', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Get authenticated user failed:', error);
    // トークン切れなどでエラーになった場合、リフレッシュを試みるなどのロジックが必要
    throw error;
  }
};

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  // 必要に応じて他のプロパティも追加
}
