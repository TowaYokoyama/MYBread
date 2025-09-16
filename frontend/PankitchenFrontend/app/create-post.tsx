import React, { useState } from 'react';
import { Text, View, TextInput, TouchableOpacity, Platform, ActivityIndicator, Alert, Image } from 'react-native'; // Image をインポート
import tw from 'twrnc';
import { useRouter } from 'expo-router';
import { createPost, uploadImage } from '../src/services/post'; // uploadImage をインポート
import * as ImagePicker from 'expo-image-picker'; // ImagePicker をインポート

export default function CreatePostScreen() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [breadType, setBreadType] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [uploadingImage, setUploadingImage] = useState(false); // 画像アップロード中のローディング状態
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  // 画像選択ハンドラ
  const pickImage = async () => {
    // メディアライブラリへのアクセス許可をリクエスト
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('パーミッションエラー', '画像を選択するにはメディアライブラリへのアクセス許可が必要です。');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setUploadingImage(true);
      try {
        const uri = result.assets[0].uri;
        const filename = uri.split('/').pop() || 'upload.jpg';
        const uploaded = await uploadImage(uri, filename);
        setImageUrl(uploaded.url);
        Alert.alert('画像アップロード', '画像が正常にアップロードされました。');
      } catch (error) {
        console.error('Image upload error:', error);
        Alert.alert('画像アップロードエラー', '画像のアップロード中にエラーが発生しました。\n' + ((error as any).response?.data?.detail || (error as any).message));
      } finally {
        setUploadingImage(false);
      }
    }
  };

  const handleCreatePost = async () => {
    if (!title.trim() || !description.trim() || !breadType.trim()) {
      Alert.alert('入力エラー', 'タイトル、内容、パンの種類をすべて入力してください。');
      return;
    }

    setLoading(true);
    try {
      const postData = {
        title,
        description,
        bread_type: breadType,
        photos: imageUrl.trim() ? [{ url: imageUrl.trim(), order: 1 }] : [],
      };
      await createPost(postData);
      Alert.alert('投稿成功', '新しい投稿が作成されました。');
      router.replace('/home');
    } catch (error) {
      console.error('Create post error:', error);
      const err = error as any;
      Alert.alert('投稿エラー', '投稿の作成中にエラーが発生しました。\n' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const containerClass = Platform.OS === 'web' ? 'w-full max-w-md mx-auto' : 'flex-1';

  return (
    <View style={tw`flex-1 justify-center p-4 bg-gray-100 ${containerClass}`}>
      <Text style={tw`text-4xl font-bold text-center text-gray-800 mb-8`}>
        新しい投稿
      </Text>

      <TextInput
        style={tw`bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mb-4`}
        placeholder="タイトル"
        value={title}
        onChangeText={setTitle}
      />

      <TextInput
        style={tw`bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mb-6 h-32`}
        placeholder="内容"
        value={description}
        onChangeText={setDescription}
        multiline
        textAlignVertical="top"
      />

      <TextInput
        style={tw`bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mb-4`}
        placeholder="パンの種類 (例: 食パン、ハード系)"
        value={breadType}
        onChangeText={setBreadType}
      />

      {/* 画像選択ボタンとプレビュー */}
      <TouchableOpacity
        style={tw`w-full bg-purple-600 rounded-lg py-3 mb-4 ${uploadingImage ? 'opacity-50' : ''}`}
        onPress={pickImage}
        disabled={uploadingImage}
      >
        {uploadingImage ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={tw`text-white text-center font-bold text-lg`}>
            画像を選択
          </Text>
        )}
      </TouchableOpacity>

      {imageUrl ? (
        <View style={tw`mb-4 items-center`}>
          <Image source={{ uri: imageUrl }} style={tw`w-48 h-48 rounded-lg`} />
          <Text style={tw`text-gray-600 text-sm mt-2`}>画像URL: {imageUrl}</Text>
        </View>
      ) : null}

      <TouchableOpacity
        style={tw`w-full bg-blue-600 rounded-lg py-3 ${loading ? 'opacity-50' : ''}`}
        onPress={handleCreatePost}
        disabled={loading || uploadingImage} // 画像アップロード中は投稿ボタンも無効化
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={tw`text-white text-center font-bold text-lg`}>
            投稿する
          </Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={tw`mt-4`}
        onPress={() => router.back()}
      >
        <Text style={tw`text-blue-600 text-center text-base`}>
          キャンセル
        </Text>
      </TouchableOpacity>
    </View>
  );
}
