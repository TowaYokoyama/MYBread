import React, { useState } from 'react';
import { Text, View, TextInput, TouchableOpacity, Platform, ActivityIndicator, Alert } from 'react-native';
import tw from 'twrnc';
import { useRouter } from 'expo-router';
import { register } from '../src/services/auth';

export default function SignUpScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSignUp = async () => {
    setLoading(true);
    try {
      const success = await register(email, password);
      if (success) {
        Alert.alert('Registration Successful', 'You can now log in with your new account.');
        router.replace('/'); // 登録成功したらログイン画面へ
      } else {
        Alert.alert('Registration Failed', 'Please try again.');
      }
    } catch (error) {
      console.error('Sign Up error:', error);
      Alert.alert('Sign Up Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const containerClass = Platform.OS === 'web' ? 'w-full max-w-md mx-auto' : 'flex-1';

  return (
    <View style={tw`justify-center p-4 bg-gray-100 ${containerClass}`}>
      <Text style={tw`text-4xl font-bold text-center text-gray-800 mb-8`}>
        Sign Up
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
        style={tw`w-full bg-green-600 rounded-lg py-3 ${loading ? 'opacity-50' : ''}`}
        onPress={handleSignUp}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={tw`text-white text-center font-bold text-lg`}>
            Sign Up
          </Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={tw`mt-4`}
        onPress={() => router.replace('/')}
      >
        <Text style={tw`text-blue-600 text-center text-base`}>
          Already have an account? Log In
        </Text>
      </TouchableOpacity>
    </View>
  );
}
