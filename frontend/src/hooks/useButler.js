/**
 * What this file does: Manages communication with the Butler agent
 * What it receives as input: User commands and agent responses
 * What it returns as output: Functions to send commands and receive agent responses
 */

import { useState, useCallback } from 'react'
import axios from 'axios'

const useButler = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendCommand = useCallback(async (command) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // TODO: Send command to backend API
      console.log('Sending command to Butler:', command)
      
      // Mock response for now
      const response = { data: { message: 'Command received' } }
      return response.data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getAgentStatus = useCallback(async () => {
    try {
      // TODO: Fetch agent status from backend
      console.log('Fetching agent status')
      return { status: 'active', lastAction: null }
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [])

  return {
    sendCommand,
    getAgentStatus,
    isLoading,
    error
  }
}

export default useButler
