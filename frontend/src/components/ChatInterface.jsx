/**
 * What this file does: Provides the chat interface for users to communicate with the Butler agent
 * What it receives as input: User messages and agent responses
 * What it returns as output: Interactive chat component with message history
 */

import React, { useState } from 'react'

const ChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')

  const handleSendMessage = () => {
    // TODO: Implement message sending logic
    console.log('Sending message:', inputMessage)
  }

  return (
    <div className="chat-interface p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-4">Chat with Butler</h3>
      <div className="message-history h-64 overflow-y-auto mb-4 p-2 bg-gray-50 rounded">
        {/* TODO: Render message history */}
      </div>
      <div className="message-input flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          className="flex-1 p-2 border rounded"
          placeholder="Tell Butler what to do..."
        />
        <button
          onClick={handleSendMessage}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatInterface
