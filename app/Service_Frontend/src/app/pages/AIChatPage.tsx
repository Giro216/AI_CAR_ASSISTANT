import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router';
import { Send, MessageSquare, Plus, ArrowLeft, Trash2, Loader2, Car, Menu } from 'lucide-react'; 
import ReactMarkdown from 'react-markdown';
import { useAuth } from '@/app/contexts/AuthContext';
import { 
  sendChatMessage, 
  apiGetConversations, 
  apiGetChatHistory, 
  apiDeleteConversation,
  ConversationOut
} from '@/app/api/chat';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messages: Message[];
  conversationId: string;
  isNew?: boolean;
}

interface RecommendedCar {
  brand_model_id: string;
  name: string;
}

const CHAT_TIMEOUT_SECONDS = 180;
const USER_ID_STORAGE_KEY = 'ai-car-user-id';

const getGuestUserId = (): string => {
  const existing = sessionStorage.getItem(USER_ID_STORAGE_KEY);
  if (existing) return existing;

  const generated = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `guest-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  sessionStorage.setItem(USER_ID_STORAGE_KEY, generated);
  return generated;
};

const createUUID = () => {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const parseRecommendations = (text: string): { cleanText: string; recommendedCars: RecommendedCar[] } => {
  const regex = /:::recommendations\s+(\[.*?\])\s*:::/s;
  const match = text.match(regex);
  
  if (match) {
    try {
      const recommendedCars = JSON.parse(match[1]) as RecommendedCar[];
      const cleanText = text.replace(regex, '').trim();
      return { cleanText, recommendedCars };
    } catch (e) {
      console.error('Ошибка парсинга JSON рекомендаций:', e);
    }
  }
  
  return { cleanText: text, recommendedCars: [] };
};

export function AIChatPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const { isAuthenticated, token } = useAuth();
  const guestUserId = getGuestUserId();

  const chatContainerRef = useRef<HTMLDivElement>(null);
  const initialMessageSentRef = useRef(false);

  const [inputValue, setInputValue] = useState('');
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(chatId || null);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [waitSeconds, setWaitSeconds] = useState(0);

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const currentChat = chats.find(chat => chat.id === currentChatId);
  const [messages, setMessages] = useState<Message[]>(currentChat?.messages || []);

  // --- Очистка гостевых диалогов из БД при закрытии вкладки ---
  useEffect(() => {
    const handleUnloadCleanup = () => {
      if (isAuthenticated) return;

      const guestId = sessionStorage.getItem(USER_ID_STORAGE_KEY);
      const guestChats: string[] = JSON.parse(sessionStorage.getItem('guest_created_conversations') || '[]');

      if (guestId && guestChats.length > 0) {
        fetch(`http://localhost:8000/api/v1/chat/conversations?user_id=${guestId}`, {
          method: 'DELETE',
          keepalive: true
        });
      }
    };

    window.addEventListener('unload', handleUnloadCleanup);
    return () => window.removeEventListener('unload', handleUnloadCleanup);
  }, [isAuthenticated]);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const serverConvs = await apiGetConversations(
          isAuthenticated ? undefined : guestUserId,
          token
        );
        
        const loadedChats: Chat[] = serverConvs.map((conv: ConversationOut) => ({
          id: conv.id,
          title: 'Загрузка...', 
          lastMessage: '',
          timestamp: new Date(conv.updated_at),
          messages: [],
          conversationId: conv.id,
          isNew: false
        }));

        setChats(prev => {
          const unsavedChats = prev.filter(c => c.isNew);
          const serverIds = new Set(loadedChats.map(c => c.id));
          const uniqueUnsaved = unsavedChats.filter(c => !serverIds.has(c.id));
          return [...uniqueUnsaved, ...loadedChats];
        });

        for (const conv of serverConvs) {
          apiGetChatHistory(conv.id, isAuthenticated ? undefined : guestUserId, token)
            .then(history => {
              const formatted = history.map((msg, idx) => ({
                id: idx,
                text: msg.content,
                sender: msg.role === 'user' ? 'user' as const : 'ai' as const,
                timestamp: new Date()
              }));

              const rawFirstMsg = formatted.find(m => m.sender === 'user')?.text || '';
              const { cleanText: firstUserMsg } = parseRecommendations(rawFirstMsg);

              const dynamicTitle = firstUserMsg 
                ? (firstUserMsg.slice(0, 25) + (firstUserMsg.length > 25 ? '...' : '')) 
                : 'Новый чат';

              const lastMsgText = formatted[formatted.length - 1]?.text || '';
              const { cleanText: cleanLastMsg } = parseRecommendations(lastMsgText);
              const formattedLastMsg = cleanLastMsg.slice(0, 35) + (cleanLastMsg.length > 35 ? '...' : '');

              setChats(prev => prev.map(chat => 
                chat.id === conv.id ? { 
                  ...chat, 
                  title: dynamicTitle,
                  lastMessage: formattedLastMsg,
                  messages: formatted
                } : chat
              ));
            })
            .catch(() => {});
        }
      } catch (err) {
        console.error('Ошибка загрузки истории чатов:', err);
      }
    };

    fetchConversations();
  }, [isAuthenticated, token]);

  // --- Загрузка истории сообщений диалога при переключении ---
  const loadChatHistory = async (convId: string) => {
    try {
      const history = await apiGetChatHistory(
        convId,
        isAuthenticated ? undefined : guestUserId,
        token
      );

      const formattedMessages: Message[] = history.map((msg, idx) => ({
        id: idx,
        text: msg.content,
        sender: msg.role === 'user' ? 'user' : 'ai',
        timestamp: new Date()
      }));

      const rawFirstMsg = formattedMessages.find(m => m.sender === 'user')?.text || '';
      const { cleanText: firstUserMsg } = parseRecommendations(rawFirstMsg);

      const dynamicTitle = firstUserMsg 
        ? (firstUserMsg.slice(0, 25) + (firstUserMsg.length > 25 ? '...' : '')) 
        : 'Новый чат';

      setMessages(formattedMessages);
      setChats(prev => prev.map(chat => 
        chat.id === convId ? { 
          ...chat, 
          messages: formattedMessages,
          title: dynamicTitle,
          lastMessage: formattedMessages[formattedMessages.length - 1]?.text || ''
        } : chat
      ));
    } catch (err) {
      console.error('Ошибка загрузки истории сообщений:', err);
    }
  };

  // --- ЕДИНЫЙ ЭФФЕКТ НАВИГАЦИИ ---
  useEffect(() => {
    if (chatId) {
      setCurrentChatId(chatId);

      const state = location.state as { initialMessage?: string } | null;
      const isInitializing = state?.initialMessage && !initialMessageSentRef.current;

      if (isInitializing) {
        return; 
      }

      setChats(prevChats => {
        const localChat = prevChats.find(c => c.id === chatId);
        if (localChat) {
          if (localChat.isNew) {
            setMessages(localChat.messages);
          } else if (localChat.messages.length > 0) {
            setMessages(localChat.messages);
          } else {
            setMessages([]);
            loadChatHistory(chatId);
          }
        } else {
          setMessages([]);
          loadChatHistory(chatId);
        }
        return prevChats;
      });
    } else {
      setCurrentChatId(null);
      setMessages([]);
    }
  }, [chatId, location.state]);

  // Скролл контейнера сообщений
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  // --- Отправка сообщения ---
  const handleSendMessage = async (forcedMessage?: string) => {
    const trimmed = (forcedMessage ?? inputValue).trim();
    if (!trimmed || isSending) return;

    const userMessage: Message = {
      id: Date.now(),
      text: trimmed,
      sender: 'user',
      timestamp: new Date(),
    };

    const activeChatId = currentChatId ?? createUUID();
    const activeChat = chats.find(chat => chat.id === activeChatId);

    setErrorMessage(null);
    setInputValue('');
    setIsSending(true);

    setMessages(prev => [...prev, userMessage]);
    
    setChats(prev => {
      const existing = prev.find(chat => chat.id === activeChatId);
      const updatedMessages = existing ? [...existing.messages, userMessage] : [userMessage];
      const updatedChat: Chat = existing
        ? {
            ...existing,
            messages: updatedMessages,
            lastMessage: userMessage.text,
            timestamp: userMessage.timestamp,
          }
        : {
            id: activeChatId,
            title: trimmed.slice(0, 25) + (trimmed.length > 25 ? '...' : ''),
            lastMessage: userMessage.text,
            timestamp: userMessage.timestamp,
            messages: updatedMessages,
            conversationId: activeChatId,
            isNew: true
          };

      return [updatedChat, ...prev.filter(chat => chat.id !== activeChatId)];
    });

    if (!currentChatId) {
      setCurrentChatId(activeChatId);
      navigate(`/chat/${activeChatId}`);

      if (!isAuthenticated) {
        const guestConvs = JSON.parse(sessionStorage.getItem('guest_created_conversations') || '[]');
        sessionStorage.setItem('guest_created_conversations', JSON.stringify([...guestConvs, activeChatId]));
      }
    }

    try {
      const response = await sendChatMessage({
        message: trimmed,
        conversation_id: activeChat?.conversationId ?? activeChatId,
        user_id: isAuthenticated ? undefined : guestUserId
      }, token);

      const aiMessage: Message = {
        id: Date.now() + 1,
        text: response.reply,
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
      setChats(prev => {
        const existing = prev.find(chat => chat.id === activeChatId);
        if (!existing) return prev;
        
        const allMsgs = [...existing.messages, aiMessage];
        const firstUserMsg = allMsgs.find(m => m.sender === 'user')?.text;
        const { cleanText: cleanTitle } = parseRecommendations(firstUserMsg || '');
        const dynamicTitle = cleanTitle 
          ? (cleanTitle.slice(0, 25) + (cleanTitle.length > 25 ? '...' : '')) 
          : 'Новый чат';

        const updatedChat: Chat = {
          ...existing,
          title: dynamicTitle,
          messages: allMsgs,
          lastMessage: aiMessage.text,
          timestamp: aiMessage.timestamp,
          conversationId: response.conversation_id,
          isNew: false
        };
        return [updatedChat, ...prev.filter(chat => chat.id !== activeChatId)];
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Не удалось получить ответ.';
      setErrorMessage(message);
    } finally {
      setIsSending(false);
    }
  };

  // --- Создание нового чата ---
  const handleNewChat = () => {
    if (!isAuthenticated && chats.length >= 3) {
      alert('Гостевой режим ограничен 3 диалогами. Зарегистрируйтесь, чтобы общаться без ограничений!');
      return;
    }

    const newChatId = createUUID();
    setCurrentChatId(newChatId);
    setMessages([]);
    setChats(prev => [
      {
        id: newChatId,
        title: 'Новый чат',
        lastMessage: '',
        timestamp: new Date(),
        messages: [],
        conversationId: newChatId,
        isNew: true
      },
      ...prev,
    ]);
    navigate(`/chat/${newChatId}`);
    setIsSidebarOpen(false);
  };

  // --- Удаление диалога ---
  const handleDeleteChat = async (convId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!window.confirm('Вы действительно хотите удалить этот диалог?')) return;

    try {
      await apiDeleteConversation(
        convId,
        isAuthenticated ? undefined : guestUserId,
        token
      );

      setChats(prev => prev.filter(c => c.id !== convId));
      
      if (!isAuthenticated) {
        const guestConvs: string[] = JSON.parse(sessionStorage.getItem('guest_created_conversations') || '[]');
        sessionStorage.setItem('guest_created_conversations', JSON.stringify(guestConvs.filter(id => id !== convId)));
      }

      if (currentChatId === convId) {
        setCurrentChatId(null);
        setMessages([]);
        navigate('/chat');
      }
    } catch (err) {
      alert('Не удалось удалить диалог');
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return 'Вчера';
    } else if (days < 7) {
      return `${days} дн. назад`;
    } else {
      return date.toLocaleDateString('ru-RU');
    }
  };

  const formatWaitTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  useEffect(() => {
    if (!isSending) {
      setWaitSeconds(0);
      return undefined;
    }

    const start = Date.now();
    const timer = window.setInterval(() => {
      const elapsed = Math.floor((Date.now() - start) / 1000);
      setWaitSeconds(Math.min(elapsed, CHAT_TIMEOUT_SECONDS));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isSending]);

  // --- Эффект первичного промпта ---
  useEffect(() => {
    const state = location.state as { initialMessage?: string } | null;
    if (!state?.initialMessage || initialMessageSentRef.current) return;

    initialMessageSentRef.current = true;
    handleSendMessage(state.initialMessage);

    navigate(location.pathname, { replace: true, state: {} });
  }, [location.state, location.pathname, navigate]);

  const progress = Math.min(waitSeconds / CHAT_TIMEOUT_SECONDS, 1);
  const circleRadius = 16;
  const circleCircumference = 2 * Math.PI * circleRadius;
  const circleOffset = circleCircumference - circleCircumference * progress;

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gray-50 overflow-hidden relative">
      {isSidebarOpen && (
        <div 
          onClick={() => setIsSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden animate-in fade-in duration-200"
        />
      )}

      <div 
        className={`
          fixed inset-y-0 left-0 z-40 w-80 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out
          lg:static lg:translate-x-0 lg:z-auto
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Новый чат</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <h3 className="px-3 py-2 text-sm text-gray-500">История чатов</h3>
            {chats.map((chat) => (
              <div key={chat.id} className="relative group">
                <Link
                  to={`/chat/${chat.id}`}
                  onClick={() => setIsSidebarOpen(false)} // Закрываем сайдбар на мобилках при выборе чата
                  className={`block px-3 py-3 mb-1 rounded-lg transition-colors pr-10 ${
                    currentChatId === chat.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <MessageSquare className="w-5 h-5 text-gray-400 mt-1 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm truncate">{chat.title}</h4>
                      <p className="text-xs text-gray-500 truncate mt-1">{chat.lastMessage}</p>
                      <p className="text-xs text-gray-400 mt-1">{formatTime(chat.timestamp)}</p>
                    </div>
                  </div>
                </Link>
                <button
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-gray-100 opacity-0 group-hover:opacity-100 lg:group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-gray-200">
          <Link
            to="/"
            onClick={() => setIsSidebarOpen(false)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>На главную</span>
          </Link>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="bg-white border-b border-gray-200 px-4 py-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3 min-w-0">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg lg:hidden transition-colors"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            <div className="min-w-0">
              <h2 className="text-lg sm:text-xl font-semibold truncate text-gray-900">
                {currentChat?.title || 'AI Помощник по подбору автомобилей'}
              </h2>
              <p className="text-xs sm:text-sm text-gray-500 truncate mt-0.5">
                Задайте вопрос, и я помогу вам найти идеальный автомобиль
              </p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div 
          ref={chatContainerRef} 
          className="flex-1 overflow-y-auto p-6 space-y-4"
        >
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageSquare className="w-16 h-16 text-gray-300 mb-4" />
              <h3 className="text-xl text-gray-600 mb-2">Начните новый диалог</h3>
              <p className="text-gray-500 max-w-md">
                Опишите ваши предпочтения, бюджет и требования к автомобилю,
                и я помогу подобрать лучшие варианты
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => {
                const { cleanText, recommendedCars } = parseRecommendations(message.text);

                return (
                  <div
                    key={message.id}
                    className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-2xl px-4 py-3 rounded-2xl ${
                        message.sender === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-gray-200'
                      }`}
                    >
                      <ReactMarkdown
                        className="text-sm leading-relaxed"
                        components={{
                          ul: ({ children }) => (
                            <ul className="list-disc pl-5 space-y-1">{children}</ul>
                          ),
                          ol: ({ children }) => (
                            <ol className="list-decimal pl-5 space-y-1">{children}</ol>
                          ),
                          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-2 border-gray-200 pl-3 italic text-gray-600">
                              {children}
                            </blockquote>
                          ),
                          code: ({ children }) => (
                            <code className="rounded bg-gray-100 px-1.5 py-0.5 text-[0.85em]">
                              {children}
                            </code>
                          ),
                          pre: ({ children }) => (
                            <pre className="overflow-x-auto rounded bg-gray-100 p-3 text-[0.85em]">
                              {children}
                            </pre>
                          ),
                        }}
                      >
                        {cleanText}
                      </ReactMarkdown>
                      <p
                        className={`text-xs mt-1 ${
                          message.sender === 'user' ? 'text-blue-100' : 'text-gray-400'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString('ru-RU', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>

                    {message.sender === 'ai' && recommendedCars.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2 max-w-2xl">
                        {recommendedCars.map((car) => (
                          <Link
                            key={car.brand_model_id}
                            to={`/catalog/${car.brand_model_id}`}
                            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-blue-50 border border-blue-200 text-blue-600 hover:bg-blue-100 rounded-xl text-sm font-medium transition-all shadow-sm hover:scale-[1.02]"
                          >
                            <Car className="w-4 h-4" />
                            <span>{car.name}</span>
                          </Link>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>

        {isSending && (
          <div className="bg-white px-6 py-4 border-t border-gray-100">
            <div className="max-w-4xl mx-auto flex flex-col items-center space-y-2 text-sm text-gray-600">
              <span className="text-xs text-gray-500">{formatWaitTime(waitSeconds)}</span>
              <div className="relative flex items-center justify-center">
                <svg width="48" height="48" className="animate-spin">
                  <circle
                    cx="24"
                    cy="24"
                    r={circleRadius + 6}
                    stroke="#E5E7EB"
                    strokeWidth="4"
                    fill="none"
                  />
                  <circle
                    cx="24"
                    cy="24"
                    r={circleRadius + 6}
                    stroke="#2563EB"
                    strokeWidth="4"
                    fill="none"
                    strokeDasharray={circleCircumference}
                    strokeDashoffset={circleOffset}
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <span>Ожидание ответа от ИИ</span>
            </div>
          </div>
        )}

        {/* Input */}
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="max-w-4xl mx-auto flex space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                maxLength={500}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Опишите ваши требования к автомобилю..."
                className="w-full pr-16 pl-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSending}
              />
              <span className="absolute right-3 bottom-3 text-xs text-gray-400">
                {inputValue.length}/500
              </span>
            </div>
            <button
              onClick={() => handleSendMessage()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed"
              disabled={isSending}
            >
              <Send className="w-5 h-5" />
              <span>Отправить</span>
            </button>
          </div>
          {errorMessage && (
            <p className="mt-3 text-sm text-red-600">{errorMessage}</p>
          )}
        </div>
      </div>
    </div>
  );
}