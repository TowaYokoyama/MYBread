import '../src/global.css'; // global.cssのインポートはここ
import { Stack, useRouter, SplashScreen } from 'expo-router';
import { useEffect, useState } from 'react';
import { getAccessToken } from '../src/services/auth'; // authサービスからトークン取得関数をインポート

// SplashScreenを非表示にする前に、すべてのリソースがロードされるのを待つ
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null); // ログイン状態を管理
  const [appIsReady, setAppIsReady] = useState(false); // アプリの準備完了状態

  useEffect(() => {
    async function prepare() {
      try {
        // トークンをチェックしてログイン状態を判定
        const token = await getAccessToken();
        setIsLoggedIn(!!token); // トークンがあればtrue、なければfalse
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true); // アプリの準備完了
        SplashScreen.hideAsync(); // スプラッシュスクリーンを非表示
      }
    }

    prepare();
  }, []);

  useEffect(() => {
    if (appIsReady) {
      // 準備完了後、ログイン状態に応じてリダイレクト
      if (isLoggedIn === false) {
        router.replace('/'); // ログインしていなければログイン画面へ
      } else if (isLoggedIn === true) {
        router.replace('/home'); // ログインしていればホーム画面へ
      }
    }
  }, [appIsReady, isLoggedIn, router]);

  if (!appIsReady) {
    return null; // アプリの準備ができていなければ何も表示しない
  }

  return (
    <Stack>
      {/* ログイン状態に応じて初期ルートを制御するため、indexとhomeは非表示 */}
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="home" options={{ headerShown: false }} />
      {/* 他の画面は通常通り表示 */}
    </Stack>
  );
}
