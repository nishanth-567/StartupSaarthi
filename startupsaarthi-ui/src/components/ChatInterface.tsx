import React, { useState } from 'react';
import { Send, Loader2, BookOpen, Languages } from 'lucide-react';
import { api, QueryResponse, Source } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

interface Message {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    sources?: Source[];
    language?: string;
    timestamp: Date;
}

const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [deterministic, setDeterministic] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!input.trim() || loading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response: QueryResponse = await api.query({
                query: input,
                deterministic,
            });

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: response.answer,
                sources: response.sources,
                language: response.detected_language,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: any) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: `Error: ${error.response?.data?.detail || error.message || 'Failed to get response'}`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header glass-card">
                <div className="header-content">
                    <div className="logo-section">
                        <BookOpen size={32} className="logo-icon" />
                        <div>
                            <h1>StartupSaarthi</h1>
                            <p className="subtitle">Your AI Guide to Indian Startup Funding</p>
                        </div>
                    </div>
                    <div className="header-controls">
                        <label className="deterministic-toggle">
                            <input
                                type="checkbox"
                                checked={deterministic}
                                onChange={(e) => setDeterministic(e.target.checked)}
                            />
                            <span>Deterministic Mode</span>
                        </label>
                        <Languages size={20} className="lang-icon" />
                    </div>
                </div>
            </div>

            <div className="messages-container">
                {messages.length === 0 && (
                    <div className="welcome-screen fade-in">
                        <h2>Welcome to StartupSaarthi! 🚀</h2>
                        <p>Ask me anything about Indian startup funding, government schemes, or investor ecosystems.</p>
                        <div className="example-queries">
                            <button onClick={() => setInput('What is SIDBI Fund of Funds?')} className="example-btn">
                                What is SIDBI Fund of Funds?
                            </button>
                            <button onClick={() => setInput('स्टार्टअप इंडिया योजना क्या है?')} className="example-btn">
                                स्टार्टअप इंडिया योजना क्या है?
                            </button>
                            <button onClick={() => setInput('List top investors in fintech')} className="example-btn">
                                List top investors in fintech
                            </button>
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <div key={message.id} className={`message ${message.type} fade-in`}>
                        <div className="message-content glass-card">
                            {message.type === 'user' ? (
                                <p>{message.content}</p>
                            ) : (
                                <>
                                    <ReactMarkdown>{message.content}</ReactMarkdown>
                                    {message.sources && message.sources.length > 0 && (
                                        <div className="sources-section">
                                            <h4>Sources:</h4>
                                            {message.sources.map((source) => (
                                                <div key={source.source_id} className="source-item">
                                                    <strong>[{source.source_id}]</strong> {source.document}
                                                    {source.page && ` - Page ${source.page}`}
                                                    {source.section && ` - ${source.section}`}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message assistant fade-in">
                        <div className="message-content glass-card loading-message">
                            <Loader2 className="spinner" size={20} />
                            <span>Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="input-container glass-card">
                <form onSubmit={handleSubmit} className="input-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about startup funding, schemes, investors..."
                        className="input message-input"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary send-btn"
                        disabled={loading || !input.trim()}
                    >
                        {loading ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
