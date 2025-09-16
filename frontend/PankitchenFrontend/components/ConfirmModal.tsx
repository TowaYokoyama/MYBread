import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import tw from 'twrnc';

interface ConfirmModalProps {
  visible: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmText?: string;
  cancelText?: string;
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({
  visible,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = 'はい',
  cancelText = 'いいえ',
}) => {
  return (
    <Modal
      transparent={true}
      animationType="fade"
      visible={visible}
      onRequestClose={onCancel}
    >
      <View style={tw`flex-1 justify-center items-center bg-black bg-opacity-50`}>
        <View style={tw`bg-white p-6 rounded-lg w-80`}>
          <Text style={tw`text-xl font-bold mb-4`}>{title}</Text>
          <Text style={tw`text-base mb-6`}>{message}</Text>
          <View style={tw`flex-row justify-end`}>
            <TouchableOpacity
              style={tw`px-4 py-2 rounded-md mr-2 bg-gray-200`}
              onPress={onCancel}
            >
              <Text style={tw`text-gray-800`}>{cancelText}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={tw`px-4 py-2 rounded-md bg-blue-500`}
              onPress={onConfirm}
            >
              <Text style={tw`text-white`}>{confirmText}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

export default ConfirmModal;
