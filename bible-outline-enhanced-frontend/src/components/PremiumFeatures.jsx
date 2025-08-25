import React, { useState } from 'react';

const PremiumFeatures = () => {
  const [email, setEmail] = useState('');
  const [isScheduled, setIsScheduled] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDownloadLatest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/download-latest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: 'en' }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Latest outline downloaded! Found ${result.references_found} verse references.`);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleWeekly = async () => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/schedule-weekly', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email,
          conference_code: 'auto'
        }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        setIsScheduled(true);
        alert(`Weekly downloads scheduled for ${email}!`);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="premium-features">
      <h2>🌟 Premium Features</h2>
      
      <div className="feature-section">
        <h3>📥 Auto-Download Latest Outlines</h3>
        <p>Automatically download and process the latest conference outlines from LSM Webcast</p>
        <button 
          onClick={handleDownloadLatest}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Downloading...' : 'Download Latest Outline'}
        </button>
      </div>

      <div className="feature-section">
        <h3>📅 Weekly Automatic Delivery</h3>
        <p>Get processed outlines delivered to your email every week</p>
        
        <div className="email-input">
          <input
            type="email"
            placeholder="Enter your email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="form-control"
          />
        </div>
        
        <button 
          onClick={handleScheduleWeekly}
          disabled={loading || isScheduled}
          className="btn btn-success"
        >
          {loading ? 'Scheduling...' : isScheduled ? 'Scheduled ✓' : 'Schedule Weekly Delivery'}
        </button>
        
        {isScheduled && (
          <p className="success-message">
            ✅ Weekly delivery scheduled! You'll receive processed outlines every Monday.
          </p>
        )}
      </div>

      <div className="feature-section">
        <h3>💎 Premium Benefits</h3>
        <ul>
          <li>✅ Automatic outline downloading from LSM Webcast</li>
          <li>✅ Weekly email delivery of processed outlines</li>
          <li>✅ Multiple language support</li>
          <li>✅ Priority customer support</li>
          <li>✅ Advanced scheduling options</li>
        </ul>
        
        <div className="pricing">
          <h4>Premium Plan: $9.99/month</h4>
          <button className="btn btn-premium">
            Upgrade to Premium
          </button>
        </div>
      </div>
    </div>
  );
};

export default PremiumFeatures;