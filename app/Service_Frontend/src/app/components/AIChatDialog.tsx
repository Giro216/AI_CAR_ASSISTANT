import { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, User as UserIcon, Sparkles, Minimize2, Maximize2 } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface AIChatDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const initialMessages: Message[] = [
  {
    id: '1',
    text: 'Здравствуйте! Я AI-помощник по подбору автомобилей. Расскажите мне о ваших предпочтениях, и я помогу найти идеальный автомобиль для вас.',
    sender: 'ai',
    timestamp: new Date(),
  },
  {
    id: '2',
    text: 'Какие характеристики для вас важны? Бюджет, тип кузова, бренд, год выпуска? Или может быть у вас есть особые требования?',
    sender: 'ai',
    timestamp: new Date(),
  },
];

const suggestionQuestions = [
  'Подобрать автомобиль до 3 млн рублей',
  'Нужен семейный внедорожник',
  'Экономичный автомобиль для города',
  'Спортивный автомобиль премиум-класса',
];

export function AIChatDialog({ isOpen, onClose }: AIChatDialogProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: getAIResponse(messageText),
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const getAIResponse = (userMessage: string) => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('бюджет') || lowerMessage.includes('млн') || lowerMessage.includes('рубл')) {
      return 'Отлично! Я подобрал для вас несколько вариантов в вашем бюджете. Какой тип кузова вы предпочитаете: седан, внедорожник, хэтчбек или купе?';
    } else if (lowerMessage.includes('внедорожник') || lowerMessage.includes('suv')) {
      return 'Прекрасный выбор! У нас есть отличные внедорожники. Рекомендую обратить внимание на Mercedes-Benz GLE, BMW X5 и Audi Q7. Какой бюджет вы рассматриваете?';
    } else if (lowerMessage.includes('семейн') || lowerMessage.includes('семь')) {
      return 'Для семейного автомобиля важны безопасность, вместительность и комфорт. Рекомендую рассмотреть внедорожники с 7 местами или просторные универсалы. Какой у вас бюджет?';
    } else if (lowerMessage.includes('спорт') || lowerMessage.includes('быстр')) {
      return 'Если вам нужен спортивный автомобиль, обратите внимание на Porsche 911, BMW M-серию или Mercedes-AMG. Это автомобили с выдающимися динамическими характеристиками. Какой бюджет вы планируете?';
    } else if (lowerMessage.includes('эконом') || lowerMessage.includes('расход')) {
      return 'Для экономичной езды рекомендую рассмотреть гибридные или электрические автомобили, такие как Tesla Model 3, Toyota Prius или Hyundai Ioniq. Также хорошим вариантом будут компактные хэтчбеки с небольшим объемом двигателя.';
    } else {
      return 'Спасибо за информацию! Чтобы подобрать идеальный автомобиль, мне нужно узнать больше деталей. Какой у вас бюджет и какие основные требования к автомобилю?';
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 animate-in fade-in duration-200">
      <div
        className={`bg-white rounded-2xl shadow-2xl w-full transition-all duration-300 ${
          isMinimized ? 'max-w-md h-20' : 'max-w-4xl h-[600px]'
        } flex flex-col overflow-hidden`}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-white">AI-помощник по подбору авто</h3>
              <p className="text-blue-100 text-sm">Онлайн</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              {isMinimized ? <Maximize2 className="w-5 h-5" /> : <Minimize2 className="w-5 h-5" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start space-x-3 ${
                    message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.sender === 'ai' ? 'bg-blue-600' : 'bg-gray-600'
                    }`}
                  >
                    {message.sender === 'ai' ? (
                      <Bot className="w-5 h-5 text-white" />
                    ) : (
                      <UserIcon className="w-5 h-5 text-white" />
                    )}
                  </div>
                  <div
                    className={`max-w-md px-4 py-3 rounded-2xl ${
                      message.sender === 'ai'
                        ? 'bg-white rounded-tl-none shadow-sm'
                        : 'bg-blue-600 text-white rounded-tr-none'
                    }`}
                  >
                    <p>{message.text}</p>
                    <span
                      className={`text-xs mt-1 block ${
                        message.sender === 'ai' ? 'text-gray-400' : 'text-blue-100'
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none shadow-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick suggestions */}
            {messages.length === 2 && (
              <div className="px-6 py-3 bg-white border-t border-gray-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span className="text-sm text-gray-600">Быстрые запросы:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {suggestionQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(question)}
                      className="px-3 py-1.5 bg-blue-50 text-blue-600 text-sm rounded-full hover:bg-blue-100 transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="bg-white border-t border-gray-200 p-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center space-x-2"
              >
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Напишите ваш запрос..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim()}
                  className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
