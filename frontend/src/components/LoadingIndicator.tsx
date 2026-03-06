import React from 'react';

const LoadingIndicator: React.FC = () => {
    return (
        <div className="flex justify-start mb-4">
            <div className="max-w-[80%] rounded-2xl rounded-bl-md px-5 py-4 bg-white/10 backdrop-blur-sm border border-white/10 shadow-lg">
                <div className="flex items-center gap-2 mb-2 text-xs font-semibold tracking-wide uppercase text-emerald-400">
                    <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] bg-emerald-500/30">
                        🤖
                    </span>
                    Jenkins AI
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                    <div className="flex gap-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-gray-500">Thinking…</span>
                </div>
            </div>
        </div>
    );
};

export default LoadingIndicator;
