import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import InputBox from './InputBox';
import LoadingIndicator from './LoadingIndicator';
import { askQuestion } from '../services/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: string[];
}

const ChatWindow: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    const handleSend = async (question: string) => {
        // Add user message
        const userMsg: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: question,
        };
        setMessages((prev) => [...prev, userMsg]);
        setIsLoading(true);

        try {
            const response = await askQuestion(question);

            const assistantMsg: Message = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response.answer,
                sources: response.sources,
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } catch (error: any) {
            const errorMsg: Message = {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: error?.response?.data?.detail
                    || error?.message
                    || 'Sorry, something went wrong. Please try again.',
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-4 py-6" id="chat-messages">
                {messages.length === 0 && !isLoading && (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-600/20 to-emerald-600/20 flex items-center justify-center mb-6 shadow-lg">
                            <span className="text-4xl">🤖</span>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Jenkins AI Assistant</h2>
                        <p className="text-gray-400 max-w-md mb-8">
                            Ask me anything about Jenkins — pipelines, plugins, configuration, troubleshooting, and more.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                            {[
                                'How do I create a Jenkins pipeline?',
                                'What is Blue Ocean in Jenkins?',
                                'How to install Jenkins plugins?',
                                'How to configure Jenkins agents?',
                            ].map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => handleSend(suggestion)}
                                    className="text-left text-sm px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20 transition-all"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg) => (
                    <ChatMessage
                        key={msg.id}
                        role={msg.role}
                        content={msg.content}
                        sources={msg.sources}
                    />
                ))}

                {isLoading && <LoadingIndicator />}

                <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <InputBox onSend={handleSend} disabled={isLoading} />
        </div>
    );
};

export default ChatWindow;
