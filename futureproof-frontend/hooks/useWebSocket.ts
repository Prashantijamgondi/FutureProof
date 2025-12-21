import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

export function useWebSocket(endpoint: string) {
    const [messages, setMessages] = useState<WebSocketMessage[]>([]);
    const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
    const ws = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

    const connect = useCallback(() => {
        try {
            const wsUrl = `${WS_URL}${endpoint}`;
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                console.log('WebSocket connected');
                setStatus('connected');
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setMessages((prev) => [...prev, data]);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setStatus('disconnected');
            };

            ws.current.onclose = () => {
                console.log('WebSocket disconnected');
                setStatus('disconnected');

                // Attempt to reconnect after 3 seconds
                reconnectTimeout.current = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 3000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            setStatus('disconnected');
        }
    }, [endpoint]);

    const sendMessage = useCallback((message: any) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        }
    }, []);

    const disconnect = useCallback(() => {
        if (reconnectTimeout.current) {
            clearTimeout(reconnectTimeout.current);
        }
        if (ws.current) {
            ws.current.close();
            ws.current = null;
        }
    }, []);

    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        messages,
        status,
        sendMessage,
        disconnect,
    };
}
