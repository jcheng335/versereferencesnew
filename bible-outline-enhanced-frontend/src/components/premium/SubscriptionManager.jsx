import React, { useState, useEffect } from 'react';

const SubscriptionManager = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const response = await fetch('/api/subscription/status');
      if (response.ok) {
        const data = await response.json();
        setSubscription(data.subscription);
      }
    } catch (error) {
      console.error('Error loading subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    try {
      const response = await fetch('/api/subscription/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, plan: 'premium' })
      });

      const result = await response.json();
      if (result.success) {
        alert('Subscription created successfully!');
        loadSubscription();
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    try {
      const response = await fetch('/api/subscription/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      if (result.success) {
        alert('Subscription cancelled successfully');
        loadSubscription();
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  if (loading) {
    return <div className="loading">Loading subscription details...</div>;
  }

  return (
    <div className="subscription-manager">
      <h2>💎 Subscription Management</h2>
      
      {!subscription ? (
        <div className="subscribe-section">
          <h3>🚀 Upgrade to Premium</h3>
          <div className="pricing-card">
            <div className="price">$9.99<span>/month</span></div>
            <ul className="features">
              <li>✅ Automatic outline downloading</li>
              <li>✅ Weekly email delivery</li>
              <li>✅ Multiple language support</li>
              <li>✅ Priority customer support</li>
              <li>✅ Advanced scheduling options</li>
            </ul>
            <div className="subscribe-form">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="email-input"
              />
              <button onClick={handleSubscribe} className="subscribe-btn">
                Subscribe Now
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="subscription-details">
          <div className="status-card">
            <h3>Current Subscription</h3>
            <div className="status-info">
              <p><strong>Plan:</strong> {subscription.plan_type}</p>
              <p><strong>Status:</strong> 
                <span className={`status ${subscription.status}`}>
                  {subscription.status}
                </span>
              </p>
              <p><strong>Started:</strong> {new Date(subscription.created_at).toLocaleDateString()}</p>
              {subscription.expires_at && (
                <p><strong>Expires:</strong> {new Date(subscription.expires_at).toLocaleDateString()}</p>
              )}
            </div>
            <button onClick={handleCancel} className="cancel-btn">
              Cancel Subscription
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionManager;