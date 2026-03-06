import React from 'react';

interface ChatMessageProps {
    role: 'user' | 'assistant';
    content: string;
    sources?: string[];
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content, sources }) => {
    const isUser = role === 'user';

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`max-w-[80%] rounded-2xl px-5 py-3.5 shadow-lg ${isUser
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-md'
                    : 'bg-white/10 backdrop-blur-sm text-gray-100 border border-white/10 rounded-bl-md'
                }`}>
                {/* Avatar & Label */}
                <div className={`flex items-center gap-2 mb-1.5 text-xs font-semibold tracking-wide uppercase ${isUser ? 'text-blue-200' : 'text-emerald-400'
                    }`}>
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${isUser ? 'bg-blue-500' : 'bg-emerald-500/30'
                        }`}>
                        {isUser ? '👤' : '🤖'}
                    </span>
                    {isUser ? 'You' : 'Jenkins AI'}
                </div>

                {/* Message Content */}
                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {content}
                </div>

                {/* Sources */}
                {sources && sources.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-white/10">
                        <p className="text-xs font-semibold text-gray-400 mb-1.5 uppercase tracking-wide">Sources</p>
                        <div className="flex flex-wrap gap-1.5">
                            {sources.map((src, i) => (
                                <a
                                    key={i}
                                    href={src}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-block text-xs px-2.5 py-1 rounded-full bg-blue-500/15 text-blue-300 hover:bg-blue-500/25 hover:text-blue-200 transition-colors truncate max-w-[200px]"
                                >
                                    {new URL(src).pathname || src}
                                </a>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatMessage;
