import React, { useState, useRef } from 'react';
import type { KeyboardEvent } from 'react';

interface InputBoxProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

const InputBox: React.FC<InputBoxProps> = ({ onSend, disabled = false }) => {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        const trimmed = input.trim();
        if (!trimmed || disabled) return;
        onSend(trimmed);
        setInput('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        // Auto-resize textarea
        const el = e.target;
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    };

    return (
        <div className="border-t border-white/10 bg-gray-900/80 backdrop-blur-md px-4 py-3">
            <div className="flex items-end gap-3 max-w-4xl mx-auto">
                <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about Jenkins pipelines, plugins, configuration…"
                    disabled={disabled}
                    rows={1}
                    className="flex-1 resize-none rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-sm text-gray-100 placeholder-gray-500 outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all disabled:opacity-50"
                    id="chat-input"
                />
                <button
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    className="flex-shrink-0 w-11 h-11 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 text-white flex items-center justify-center hover:from-blue-500 hover:to-blue-600 transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20"
                    id="send-button"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                </button>
            </div>
            <p className="text-center text-xs text-gray-600 mt-2">
                Press Enter to send · Shift+Enter for new line
            </p>
        </div>
    );
};

export default InputBox;
