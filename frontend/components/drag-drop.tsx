"use client";

import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { message, Upload } from 'antd';
import '@ant-design/v5-patch-for-react-19';

const { Dragger } = Upload;

const props: UploadProps = {
  name: 'file',
  multiple: false,
  action: 'http://localhost:8000/upload',
  headers: {
    'Accept': 'application/json',
  },
  beforeUpload: (file) => {
    // Log the file being uploaded
    console.log('File to be uploaded:', file);
    
    const isValidFile = file.type === 'application/pdf' || 
                        file.type.startsWith('image/') ||
                        file.type === 'application/msword' ||
                        file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    if (!isValidFile) {
      message.error('You can only upload PDF, image, or document files!');
    }
    return isValidFile || Upload.LIST_IGNORE;
  },
  onChange(info) {
    const { status } = info.file;
    
    // Log detailed request information
    console.log('Upload status:', status);
    console.log('Full upload info:', info);
    
    if (status !== 'uploading') {
      console.log(info.file, info.fileList);
    }
    if (status === 'done') {
      console.log('Server response:', info.file.response);
      message.success(`${info.file.name} file uploaded successfully.`);
    } else if (status === 'error') {
      console.error('Upload error details:', info.file.response);
      console.error('HTTP status:', info.file.xhr?.status);
      console.error('Response text:', info.file.xhr?.responseText);
      message.error(`${info.file.name} file upload failed: ${info.file.response?.message || 'Unknown error'}`);
    }
  },
  onDrop(e) {
    console.log('Dropped files', e.dataTransfer.files);
  },
  // Enable debug mode to see request details in browser console
};

export const DragNDrop = () => {
  return (
    <Dragger {...props}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">Click or drag file to this area to upload</p>
      <p className="ant-upload-hint">
        Support for PDF, image, and document files. Strictly prohibited from uploading company data or other
        banned files.
      </p>
    </Dragger>
  );
};