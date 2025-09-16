import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, FlatList, ActivityIndicator, Alert, Image } from 'react-native';
import tw from 'twrnc';
import { useRouter } from 'expo-router';
import { getAllPosts, deletePost, Post } from '../src/services/post';
import { getAuthenticatedUser, clearTokens,User } from '../src/services/auth';
import ConfirmModal from '../components/ConfirmModal'; // ConfirmModal をインポート

export default function HomeScreen() {
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false); // 削除確認モーダルの表示状態
  const [postToDelete, setPostToDelete] = useState<number | null>(null); // 削除対象の投稿ID
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false); // ログアウト確認モーダルの表示状態

  // 投稿を取得する関数
  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      const fetchedPosts = await getAllPosts();
      setPosts(fetchedPosts);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      Alert.alert('エラー', '投稿の取得に失敗しました。');
    } finally {
      setLoading(false);
    }
  }, []);

  // 現在のユーザー情報を取得する関数
  const fetchCurrentUser = useCallback(async () => {
    try {
      const user = await getAuthenticatedUser();
      setCurrentUser(user);
      console.log('Current User:', user); // デバッグログを追加
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      // ユーザー情報が取得できない場合はログイン画面に戻す
      router.replace('/');
    }
  }, [router]); // router を依存配列に追加

  useEffect(() => {
    fetchCurrentUser(); // ユーザー情報を取得
    fetchPosts(); // 投稿を取得
  }, [fetchCurrentUser, fetchPosts]);

  // 投稿削除ハンドラ (モーダル表示用)
  const handleDeletePost = (postId: number) => {
    console.log('Delete button pressed for post ID:', postId);
    setPostToDelete(postId);
    setShowDeleteConfirm(true); // モーダルを表示
  };

  // 実際の削除処理
  const confirmDelete = async () => {
    if (postToDelete === null) return;

    setShowDeleteConfirm(false); // モーダルを閉じる
    try {
      await deletePost(postToDelete);
      Alert.alert('成功', '投稿が削除されました。');
      fetchPosts(); // 投稿リストを再取得して更新
    } catch (error) {
      console.error('Delete post error:', error);
      const err = error as any;
      Alert.alert('エラー', '投稿の削除に失敗しました。' + (err.response?.data?.detail || err.message));
    }
  };

  // ログアウトハンドラ (モーダル表示用)
  const handleLogout = () => {
    setShowLogoutConfirm(true); // モーダルを表示
  };

  // 実際のログアウト処理
  const confirmLogout = async () => {
    setShowLogoutConfirm(false); // モーダルを閉じる
    try {
      await clearTokens(); // トークンをクリア
      router.replace('/'); // ログイン画面へリダイレクト
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('エラー', 'ログアウト中にエラーが発生しました。');
    }
  };

  const renderPostItem = ({ item }: { item: Post }) => {
    console.log('Post Item:', item); // デバッグログを追加
    console.log('Current User ID:', currentUser?.id, 'Post User ID:', item.user_id); // デバッグログを追加
    return (
      <View style={tw`bg-white p-4 rounded-lg shadow-md mb-4 w-full`}>
        <Text style={tw`text-xl font-bold mb-2`}>{item.title}</Text>
        <Text style={tw`text-gray-700 mb-1`}>{item.description}</Text>
        <Text style={tw`text-gray-500 text-sm`}>種類: {item.bread_type}</Text>
        {item.photos && item.photos.length > 0 && (
          <Image
            source={{ uri: item.photos[0].url }}
            style={tw`w-full h-48 rounded-lg mt-2`}
          />
        )}
        {currentUser && currentUser.id === item.user_id && (
          <TouchableOpacity
            style={tw`mt-2 bg-red-500 px-3 py-1 rounded-md self-end`}
            onPress={() => handleDeletePost(item.id)}
          >
            <Text style={tw`text-white text-sm`}>削除</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={tw`flex-1 justify-center items-center bg-blue-100`}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={tw`mt-2 text-lg text-gray-700`}>投稿を読み込み中...</Text>
      </View>
    );
  }

  return (
    <View style={tw`flex-1 p-4 bg-blue-100`}>
      <View style={tw`flex-row justify-between items-center mb-4`}>
        <Text style={tw`text-3xl font-bold text-blue-800`}>タイムライン</Text>
        <TouchableOpacity
          style={tw`bg-green-500 px-4 py-2 rounded-lg`}
          onPress={() => router.push('/create-post')}
        >
          <Text style={tw`text-white text-lg font-bold`}>新規投稿</Text>
        </TouchableOpacity>
        {/* ログアウトボタンを追加 */}
        <TouchableOpacity
          style={tw`bg-gray-500 px-4 py-2 rounded-lg`}
          onPress={handleLogout}
        >
          <Text style={tw`text-white text-lg font-bold`}>ログアウト</Text>
        </TouchableOpacity>
      </View>

      {posts.length === 0 ? (
        <View style={tw`flex-1 justify-center items-center`}>
          <Text style={tw`text-xl text-gray-600`}>まだ投稿がありません。</Text>
          <Text style={tw`text-md text-gray-500 mt-2`}>最初の投稿をしてみましょう！</Text>
        </View>
      ) : (
        <FlatList
          data={posts}
          renderItem={renderPostItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={tw`py-2`}
        />
      )}

      {/* 削除確認モーダル */}
      <ConfirmModal
        visible={showDeleteConfirm}
        title="投稿の削除"
        message="本当にこの投稿を削除しますか？"
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        confirmText="削除"
        cancelText="キャンセル"
      />

      {/* ログアウト確認モーダル */}
      <ConfirmModal
        visible={showLogoutConfirm}
        title="ログアウト"
        message="本当にログアウトしますか？"
        onConfirm={confirmLogout}
        onCancel={() => setShowLogoutConfirm(false)}
        confirmText="ログアウト"
        cancelText="キャンセル"
      />
    </View>
  );
}