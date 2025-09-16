import React, { useState } from 'react';
import { Text, View, TextInput, TouchableOpacity, Platform, ActivityIndicator, Alert } from 'react-native';
import tw from 'twrnc';
import { useRouter } from 'expo-router'; // useRouterをインポート
import { login } from '../src/services/auth'; // authサービスをインポート

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false); // ローディング状態
  const router = useRouter(); // useRouterフックを使用

  const handleLogin = async () => {
    setLoading(true); // ローディング開始
    try {
      const success = await login(email, password);
      if (success) {
        router.replace('/home'); // ログイン成功したらホーム画面へ
      } else {
        Alert.alert('Login Failed', 'Invalid credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Login Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false); // ローディング終了
    }
  };

  // A simple platform-specific style adjustment for the container
  const containerClass = Platform.OS === 'web' ? 'w-full max-w-md mx-auto' : 'flex-1';

  return (
    <View style={tw`justify-center p-4 bg-gray-100 ${containerClass}`}>
      <Text style={tw`text-4xl font-bold text-center text-gray-800 mb-8`}>
        Pankitchen
      </Text>
      
      <TextInput
        style={tw`bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mb-4`}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      
      <TextInput
        style={tw`bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 mb-6`}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TouchableOpacity
        style={tw`w-full bg-blue-600 rounded-lg py-3 ${loading ? 'opacity-50' : ''}`}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={tw`text-white text-center font-bold text-lg`}>
            Login
          </Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={tw`mt-4`}
        onPress={() => router.replace('/signup')}
      >
        <Text style={tw`text-blue-600 text-center text-base`}>
          Don't have an account? Sign Up
        </Text>
      </TouchableOpacity>
    </View>
  );
}