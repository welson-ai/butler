/**
 * What this file does: Displays live agent actions and transaction updates
 * What it receives as input: Real-time activity data from WebSocket
 * What it returns as output: Feed showing recent Butler actions
 */

import React, { useState, useEffect } from 'react'

const ActivityFeed = () => {
  const [activities, setActivities] = useState([])

  useEffect(() => {
    // TODO: Connect to WebSocket for real-time updates
    console.log('Setting up activity feed WebSocket connection')
  }, [])

  return (
    <div className="activity-feed p-4 border rounded-lg">
      <h3 className="text-lg font-bold mb-4">Live Activity</h3>
      <div className="activity-list space-y-2">
        {activities.length === 0 ? (
          <p className="text-gray-500">No recent activity</p>
        ) : (
          // TODO: Render activity items
          activities.map((activity, index) => (
            <div key={index} className="activity-item p-2 bg-gray-50 rounded">
              {/* TODO: Display activity details */}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ActivityFeed
