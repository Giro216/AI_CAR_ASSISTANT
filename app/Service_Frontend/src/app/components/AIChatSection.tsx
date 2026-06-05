// src/app/components/AIChatSection.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Send, Bot } from 'lucide-react';

// Генератор UUID для нового диалога
const createUUID = () => {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export function AIChatSection() {
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = message.trim();
    if (!trimmed) return;

    // Генерируем UUID диалога сразу на главном экране
    const newConversationId = createUUID();

    // Перенаправляем пользователя сразу на уникальный роут диалога
    navigate(`/chat/${newConversationId}`, { state: { initialMessage: trimmed } });
    setMessage('');
  };

  return (
    <section className="py-12 px-4 bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl mb-2">Помощник по подбору автомобиля</h2>
          <p className="text-gray-600">
            Расскажите о своих предпочтениях, и наша нейросеть подберет идеальный автомобиль
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6">
          {/* Chat Messages */}
          <div className="mb-6 space-y-4 max-h-96 overflow-y-auto">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 max-w-md">
                <p className="text-gray-800">
                  Здравствуйте! Я помогу вам подобрать автомобиль. Расскажите, какие характеристики для вас важны?
                </p>
              </div>
            </div>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex items-center space-x-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Напишите ваши пожелания..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}