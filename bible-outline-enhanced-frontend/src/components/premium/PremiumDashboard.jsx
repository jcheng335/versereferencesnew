import React, { useState, useEffect } from 'react';
import './PremiumDashboard.css';
import { getApiUrl } from '@/config/api';

const PremiumDashboard = () => {
  const [userPlan, setUserPlan] = useState('free');
  const [scheduledTasks, setScheduledTasks] = useState([]);
  const [conferences, setConferences] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUserData();
    loadConferences();
  }, []);

  const loadUserData = async () => {
    try {
      // Load user subscription and scheduled tasks
      const response = await fetch(getApiUrl('user/subscription'));
      if (response.ok) {
        const data = await response.json();
        setUserPlan(data.plan || 'free');
        setScheduledTasks(data.scheduled_tasks || []);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const loadConferences = async () => {
    try {
      const response = await fetch(getApiUrl('conferences'));
      if (response.ok) {
        const data = await response.json();
        setConferences(data.conferences || []);
      }
    } catch (error) {
      console.error('Error loading conferences:', error);
    }
  };

  const handleUpgrade = () => {
    // Redirect to payment/upgrade page
    window.open('https://checkout.stripe.com/premium-plan', '_blank');
  };

  const handleDownloadLatest = async () => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl('download-latest'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'en' })
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`✅ Latest outline downloaded! Found ${result.references_found} verse references.`);
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleWeekly = async (email) => {
    try {
      const response = await fetch(getApiUrl('schedule-weekly'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, conference_code: 'auto' })
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`✅ Weekly delivery scheduled for ${email}!`);
        loadUserData(); // Refresh tasks
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    }
  };

  return (
    <div className="premium-dashboard">
      <div className="dashboard-header">
        <h1>🌟 Premium Dashboard</h1>
        <div className="plan-badge">
          <span className={`badge ${userPlan}`}>
            {userPlan === 'premium' ? '💎 Premium' : '🆓 Free'}
          </span>
        </div>
      </div>

      {userPlan === 'free' && (
        <div className="upgrade-banner">
          <div className="upgrade-content">
            <h2>🚀 Upgrade to Premium</h2>
            <p>Unlock automatic outline downloading, weekly email delivery, and advanced features!</p>
            <div className="features-grid">
              <div className="feature">
                <span className="icon">📥</span>
                <span>Auto-download from LSM Webcast</span>
              </div>
              <div className="feature">
                <span className="icon">📧</span>
                <span>Weekly email delivery</span>
              </div>
              <div className="feature">
                <span className="icon">🌍</span>
                <span>Multiple language support</span>
              </div>
              <div className="feature">
                <span className="icon">⚡</span>
                <span>Priority processing</span>
              </div>
            </div>
            <button className="upgrade-btn" onClick={handleUpgrade}>
              Upgrade to Premium - $9.99/month
            </button>
          </div>
        </div>
      )}

      <div className="dashboard-grid">
        <div className="card">
          <h3>📥 Quick Download</h3>
          <p>Download and process the latest conference outline</p>
          <button 
            className="btn btn-primary" 
            onClick={handleDownloadLatest}
            disabled={loading || userPlan === 'free'}
          >
            {loading ? 'Downloading...' : 'Download Latest Outline'}
          </button>
          {userPlan === 'free' && (
            <p className="premium-required">Premium required</p>
          )}
        </div>

        <div className="card">
          <h3>📅 Scheduled Tasks</h3>
          {scheduledTasks.length > 0 ? (
            <div className="tasks-list">
              {scheduledTasks.map(task => (
                <div key={task.id} className="task-item">
                  <span className="task-type">{task.task_type}</span>
                  <span className="task-frequency">{task.frequency}</span>
                  <span className="task-next">Next: {new Date(task.next_run).toLocaleDateString()}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>No scheduled tasks</p>
          )}
        </div>

        <div className="card">
          <h3>🎯 Available Conferences</h3>
          <div className="conferences-list">
            {conferences.map(conf => (
              <div key={conf.code} className="conference-item">
                <h4>{conf.title}</h4>
                <p>📅 {conf.date} • 📝 {conf.message_count} messages</p>
                <button 
                  className="btn btn-secondary"
                  disabled={userPlan === 'free'}
                >
                  Schedule Auto-Download
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PremiumDashboard;