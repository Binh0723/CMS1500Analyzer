import React, { useState, useRef } from 'react';
import { BeRequest } from '../services/BeRequest'
import {ChatRequest, InitialChatRequest} from '../services/ChatRequest'
// Define TypeScript interfaces
export interface AnalysisResult {
  errors: { field: string; message: string }[];

}

interface ChatMessage {
  sender: 'user' | 'system';
  message: string;
  timestamp: Date;
}


const CMS1500Analyzer: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<string | null >(null)
  const [preview, setPreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      sender: 'system',
      message: 'Upload a CMS-1500 form to begin analysis.',
      timestamp: new Date(),
    },
  ]);
  const [userMessage, setUserMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      
      // Create preview for image files
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        setFileType("image")
        reader.onload = (e) => {
          if (e.target?.result) {
            setPreview(e.target.result as string);
          }
        };
        reader.readAsDataURL(file);
      } else if (file.type === 'application/pdf') {
        // For demonstration purposes, we'll just show a PDF icon
        const reader = new FileReader();
        setFileType("pdf");
        reader.onload = () => {
          const blob = new Blob([reader.result as ArrayBuffer], { type: "application/pdf" });
          const url = URL.createObjectURL(blob);
          setPreview(url);
        };
        reader.readAsArrayBuffer(file);
      }
      
      // In a real app, this would call your backend API for analysis
     await sendRequestToBackEnd(file)

    }
  };
  const sendInitialRequestToBackEnd = async (analysisResult : AnalysisResult)=>{
      const response = await InitialChatRequest(analysisResult)
      return response
  }
   const sendRequestToBackEnd = async (file: File): Promise<AnalysisResult>=>{
    console.log("inside send request to be")
    console.log("sending image/pdf to be")
    const response = await BeRequest(file)
    const converted: AnalysisResult = {
      errors: response.result.map((item: any) => ({
        field: item.field,
        message: item.error,
      })),
    };
    setAnalysis(converted);
    const json_response = JSON.stringify(response)

    console.log("send image to back end successfully " + json_response)
    const initialResponse:any = await sendInitialRequestToBackEnd(converted)
    if (initialResponse && typeof initialResponse === 'object' && 'Message' in initialResponse) {
      addSystemMessage(initialResponse?.result?.Message); 
    } 
    else if(typeof initialResponse ==='string'){
      addSystemMessage(initialResponse)
    }
    return response
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      
      // Create preview
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        setFileType("image");

        reader.onload = (e) => {
          if (e.target?.result) {
            setPreview(e.target.result as string);
          }
        };
        reader.readAsDataURL(file);
      } else if (file.type === 'application/pdf') {
        const reader = new FileReader();
        setFileType("pdf");
        reader.onload = () => {
          const blob = new Blob([reader.result as ArrayBuffer], { type: "application/pdf" });
          const url = URL.createObjectURL(blob);
          setPreview(url); // Use in <iframe src={preview} />
        };
        reader.readAsArrayBuffer(file);
      }
      await sendRequestToBackEnd(file)

    }
  };

 

  const addSystemMessage = (message: string) => {
    setChatMessages(prev => [
      ...prev,
      {
        sender: 'system',
        message,
        timestamp: new Date()
      }
    ]);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userMessage.trim()) return;
    
    // Add user message to chat
    setChatMessages(prev => [
      ...prev, 
      {
        sender: 'user',
        message: userMessage,
        timestamp: new Date()
      }
    ]);
    
    // Simulate response (in a real app, this would call your backend API)
    setTimeout(() => {
      addSystemMessage(`Thank you for your question about "${userMessage}". For CMS-1500 forms, please ensure all required fields are properly filled and diagnosis codes match the current ICD-10 format.`);
    }, 1000);
    
    setUserMessage('');
  };

  // Scroll chat to bottom when new messages arrive
  React.useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">CMS-1500 Form Analyzer</h1>
      </header>
      
      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Form upload */}
        <div className="w-1/2 p-4 flex flex-col bg-white border-r border-gray-200">
          <div 
            className="flex-1 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center p-4 overflow-auto"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {preview ? (
              <div className="w-full h-full flex flex-col items-center">
                {/* <img 
                  src={preview} 
                  alt="CMS-1500 Preview" 
                  className="max-w-full max-h-full object-contain mb-4"
                /> */}
                {fileType === "image" && <img src={preview} 
                  alt="CMS-1500 Preview" 
                  className="max-w-full max-h-full object-contain mb-4"/>}
                {fileType === 'pdf' && <iframe src={preview} width="100%" height="600px" title="PDF Preview" />
              }
                <div className="flex space-x-4">
                  <button 
                    onClick={() => {
                      setSelectedFile(null);
                      setPreview(null);
                      setAnalysis(null);
                    }}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md"
                  >
                    Remove
                  </button>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
                  >
                    Upload New
                  </button>
                </div>
              </div>
            ) : (
              <>
                <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-gray-500 mb-4 text-center">Drag and drop your CMS-1500 form here, or click to select a file</p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
                >
                  Select File
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept="image/*,application/pdf"
                  onChange={handleFileUpload}
                />
                <p className="text-sm text-gray-400 mt-2">Supports PDF and image files</p>
              </>
            )}
          </div>
        </div>
        
        {/* Right panel - Analysis results */}
        <div className="w-1/2 bg-gray-50 flex flex-col">
          {/* Analysis results section */}
          <div className="p-4 overflow-auto flex-1">
            <h2 className="text-xl font-semibold mb-4">Form Analysis</h2>
            
            {!analysis && !selectedFile && (
              <div className="bg-blue-50 border-l-4 border-blue-500 text-blue-700 p-4 rounded">
                <p>Upload a CMS-1500 form to see the analysis results here.</p>
              </div>
            )}
            
            {!analysis && selectedFile && (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
                <span className="ml-3 text-gray-600">Analyzing form...</span>
              </div>
            )}
            
            {analysis && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-red-600 mb-2">  Errors Found ({analysis?.errors?.length ?? 0})
                  </h3>
                  {analysis?.errors?.map((error, index) => (
                    <div key={`error-${index}`} className="bg-red-50 border-l-4 border-red-500 p-3 mb-2 rounded">
                      <span className="font-medium">{error.field}:</span> {error.message}
                    </div>
                  ))}
                </div>
                
              </div>
            )}
          </div>
          
          {/* Chat section */}
          <div className="border-t border-gray-200 bg-white p-4 flex flex-col h-1/2">
            <h2 className="text-lg font-semibold mb-2">Help & Suggestions</h2>
            
            {/* Chat messages */}
            <div 
              ref={chatContainerRef}
              className="flex-1 overflow-y-auto mb-4 p-2"
            >
              {chatMessages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`mb-2 p-3 rounded-lg max-w-xs ${
                    msg.sender === 'user' 
                      ? 'bg-blue-100 ml-auto' 
                      : 'bg-gray-100'
                  }`}
                >
                  <p className="text-sm">{msg.message}</p>
                  <span className="text-xs text-gray-500">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
            
            {/* Message input */}
            <form onSubmit={handleSendMessage} className="flex">
              <input
                type="text"
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                className="flex-1 border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ask a question about your form..."
              />
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-r-md"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CMS1500Analyzer;