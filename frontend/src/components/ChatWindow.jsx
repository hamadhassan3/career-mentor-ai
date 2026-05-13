import { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../config/api-backend';

const ChatWindow = ({ isOpen, onClose, userName }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatRef = useRef(null);
  
  const avatarName = process.env.REACT_APP_AVATAR_NAME || 'Fawkes';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const loadConversationHistory = async () => {
      if (isOpen && messages.length === 0) {
        try {
          const response = await chatAPI.getConversationHistory();
          const data = response.data;
          
          if (data.conversation_id && data.messages.length > 0) {
            setConversationId(data.conversation_id);
            
            // Convert backend messages to frontend format
            const formattedMessages = data.messages.map((msg, index) => ({
              id: Date.now() + index,
              text: msg.content,
              sender: msg.role === 'user' ? userName || 'User' : avatarName,
              timestamp: msg.created_at,
              isUser: msg.role === 'user'
            }));
            
            setMessages(formattedMessages);
          }
        } catch (error) {
          console.error('Error loading conversation history:', error);
        }
      }
    };

    loadConversationHistory();
  }, [isOpen, messages.length, userName, avatarName]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatRef.current && !chatRef.current.contains(event.target)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: currentMessage.trim(),
      sender: userName || 'User',
      timestamp: new Date().toISOString(),
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        message: userMessage.text,
        conversation_id: conversationId
      });

      const data = response.data;
      
      setConversationId(data.conversation_id);
      
      const aiMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: avatarName,
        timestamp: new Date().toISOString(),
        isUser: false
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: avatarName,
        timestamp: new Date().toISOString(),
        isUser: false,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };


  return (
    <>
      {/* Backdrop for mobile */}
      <div 
        className={`fixed inset-0 z-50 bg-black transition-opacity duration-300 sm:hidden ${
          isOpen ? 'opacity-50' : 'opacity-0 pointer-events-none'
        }`}
      />
      
      {/* Chat Container */}
      <div 
        className={`fixed z-50 transition-all duration-300 ease-out ${
          isOpen 
            ? 'opacity-100 translate-y-0' 
            : 'opacity-0 translate-y-full pointer-events-none'
        } 
        inset-0 h-screen sm:inset-auto sm:bottom-6 sm:right-2 sm:h-[90vh] sm:w-[380px] md:w-[420px]`}
      >
        <div 
          ref={chatRef}
          className="bg-white rounded-none sm:rounded-lg shadow-xl border border-gray-200 h-full flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-1 border-b border-gray-100 bg-white rounded-t-none sm:rounded-t-lg flex-shrink-0 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="w-14 h-14 rounded-full overflow-hidden bg-indigo-100 flex-shrink-0">
                <img
                  src="/avatar/listening.png"
                  alt={avatarName}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-gray-900 truncate">{avatarName}</h3>
                <p className="text-xs text-gray-500">Career Mentor</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-500 hover:text-gray-700"
              aria-label="Close chat"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50 min-h-0">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8 sm:mt-12">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-indigo-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <p className="text-sm">Ask me about your career path!</p>
              </div>
            )}
            
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[280px] px-3 py-2 rounded-2xl text-sm ${
                      message.isUser
                        ? 'bg-indigo-600 text-white rounded-br-md'
                        : message.isError
                        ? 'bg-red-100 text-red-800 rounded-bl-md'
                        : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm'
                    }`}
                  >
                    <p className="leading-relaxed">{message.text}</p>
                    <div className={`text-xs mt-1 ${
                      message.isUser ? 'text-indigo-100' : 'text-gray-500'
                    } ${message.isUser ? 'text-right' : 'text-left'}`}>
                      <span className="font-medium">{message.sender}</span>
                      <span className="ml-1">{formatTime(message.timestamp)}</span>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] sm:max-w-[280px] px-3 py-2 rounded-2xl rounded-bl-md bg-white border border-gray-200 shadow-sm">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-600">{avatarName} is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 bg-white border-t border-gray-100 rounded-b-none sm:rounded-b-lg flex-shrink-0">
            <form onSubmit={sendMessage} className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder={`Ask ${avatarName}...`}
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!currentMessage.trim() || isLoading}
                className={`px-4 py-2 rounded-lg transition-colors flex-shrink-0 ${
                  !currentMessage.trim() || isLoading
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500'
                }`}
                aria-label="Send message"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default ChatWindow;