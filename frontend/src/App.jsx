import React, { useState, useEffect } from 'react';
import PersonaCard from './components/PersonaCard';
import RecommendationEngine from './components/RecommendationEngine';
import NeuralPipeline from './components/NeuralPipeline';
import ReviewDisplay from './components/ReviewDisplay';
import './App.css';

const API_BASE = '/api';

function App() {
  const [activeTab, setActiveTab] = useState('home'); // home, pool, taskB, taskA
  const [personas, setPersonas] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(true);
  
  // Pool State
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  
  // Column 2 State (Task B)
  const [recommendations, setRecommendations] = useState([]);
  const [isRecLoading, setIsRecLoading] = useState(false);
  const [recErrorStr, setRecErrorStr] = useState('');

  // Column 3 State (Task A)
  const [simulation, setSimulation] = useState(null);
  const [dna, setDna] = useState(null);
  const [isSimLoading, setIsSimLoading] = useState(false);
  const [simErrorStr, setSimErrorStr] = useState('');
  const [isStreamingComplete, setIsStreamingComplete] = useState(false);
  const [manualProduct, setManualProduct] = useState('');
  const [manualAttrs, setManualAttrs] = useState('');
  
  useEffect(() => {
    // Apply theme class to body
    if (isDarkMode) {
      document.body.classList.remove('light-theme');
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
      document.body.classList.add('light-theme');
    }
  }, [isDarkMode]);

  useEffect(() => {
    fetch(`${API_BASE}/users?limit=500`)
      .then(res => res.json())
      .then(data => setPersonas(data.users || []))
      .catch(err => console.error("Failed to fetch users", err));
  }, []);

  const handleSelectPersona = async (p) => {
    setSelectedPersona(p);
    
    // Reset Task A Col
    setSimulation(null);
    setDna(null);
    setSimErrorStr('');
    setIsStreamingComplete(false);

    // Trigger Task B (Recommendations)
    setIsRecLoading(true);
    setRecommendations([]);
    setRecErrorStr('');
    
    try {
      const response = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: p.user_id, api_key: '' }) // Relies on server ENV
      });
      
      const data = await response.json();
      if (response.ok) {
        setRecommendations(data.recommendations || []);
      } else {
        setRecErrorStr(data.detail);
      }
    } catch (err) {
      setRecErrorStr(err.message);
    } finally {
      setIsRecLoading(false);
    }
    
    // Switch to Task B
    setActiveTab('taskB');
  };

  const triggerSimulation = async (product_name, product_attrs) => {
    setActiveTab('taskA');
    if (!selectedPersona || !product_name) return;
    
    setIsSimLoading(true);
    setSimulation(null);
    setDna(null);
    setSimErrorStr('');
    setIsStreamingComplete(false);
    
    try {
      const response = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: selectedPersona.user_id, 
          product_name: product_name,
          product_attributes: product_attrs,
          api_key: '' // Relies on server ENV
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        setSimulation(data);
        setDna(data.dna);
      } else {
        setSimErrorStr(data.detail);
      }
    } catch (err) {
      setSimErrorStr(err.message);
    } finally {
      setIsSimLoading(false);
    }
  };

  const handleManualSimulate = () => {
    triggerSimulation(manualProduct, manualAttrs);
  };

  const filteredPersonas = personas.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;
    
    if (activeFilter === '> 50 Reviews') return parseInt(p.review_count) > 50;
    if (activeFilter === '> 100 Reviews') return parseInt(p.review_count) > 100;
    if (activeFilter === '> 500 Reviews') return parseInt(p.review_count) > 500;
    return true; // 'All'
  });

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <header className="top-nav">
        <div className="brand-logo">
          <img src="/logo.svg" alt="Vorge Logo" />
          <h1>Vorge.</h1>
        </div>
        <div className="nav-tabs">
          <button className={`nav-tab ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>Home</button>
          <button className={`nav-tab ${activeTab === 'pool' ? 'active' : ''}`} onClick={() => setActiveTab('pool')}>The Mind Pool</button>
          <button className={`nav-tab ${activeTab === 'taskB' ? 'active' : ''}`} onClick={() => setActiveTab('taskB')}>Recommender</button>
          <button className={`nav-tab ${activeTab === 'taskA' ? 'active' : ''}`} onClick={() => setActiveTab('taskA')}>Simulator</button>
        </div>
        <button className="theme-toggle" onClick={() => setIsDarkMode(!isDarkMode)}>
          {isDarkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
      </header>

      {/* Main Content Area */}
      {activeTab === 'home' && (
        <div className="home-hero">
          <h1>Predict Human Behavior.</h1>
          <p>
            Vorge distills unstructured historical data into high-fidelity "Behavioral DNA". 
            Our proprietary three-stage adversarial pipeline mathematically predicts how any 
            human profile will react to completely unprecedented, cross-domain stimuli.
          </p>
          <button className="hero-btn" onClick={() => setActiveTab('pool')}>Explore The Mind Pool</button>
        </div>
      )}

      {activeTab === 'pool' && (
        <div className="page-view">
          <div className="page-header">
            <h2>The Mind Pool</h2>
            <p>Select a persona. We will extract their DNA to generate cross-domain product recommendations.</p>
          </div>
          
          <div className="pool-controls">
            <input 
              type="text" 
              placeholder="Search for a specific behavior profile..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="filter-pills">
              {['All', '> 50 Reviews', '> 100 Reviews', '> 500 Reviews'].map(f => (
                <button 
                  key={f} 
                  className={`filter-pill ${activeFilter === f ? 'active' : ''}`}
                  onClick={() => setActiveFilter(f)}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          
          <div className="persona-grid">
            {filteredPersonas.map(p => (
              <PersonaCard 
                key={p.user_id} 
                persona={p} 
                isSelected={selectedPersona?.user_id === p.user_id}
                onClick={() => handleSelectPersona(p)}
              />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'taskB' && (
        <div className="page-view">
          {!selectedPersona ? (
            <div className="empty-tab-state">
              <h2>Awaiting Subject</h2>
              <p>Please select a human from the Mind Pool to generate tailored recommendations.</p>
              <button className="btn-goto-pool" onClick={() => setActiveTab('pool')}>Go to Pool</button>
            </div>
          ) : (
            <>
              <div className="page-header">
                <h2>Cross-Domain Recommender</h2>
                <p>Analyzing behavioral vectors for {selectedPersona.name} to invent tailored products.</p>
              </div>
              <RecommendationEngine 
                recommendations={recommendations} 
                isLoading={isRecLoading}
                errorStr={recErrorStr}
                onSimulate={triggerSimulation}
              />
            </>
          )}
        </div>
      )}

      {activeTab === 'taskA' && (
        <div className="page-view" style={{maxWidth: '1000px', margin: '0 auto'}}>
          {!selectedPersona ? (
            <div className="empty-tab-state">
              <h2>Awaiting Subject</h2>
              <p>Please select a human from the Mind Pool to run a behavioral simulation.</p>
              <button className="btn-goto-pool" onClick={() => setActiveTab('pool')}>Go to Pool</button>
            </div>
          ) : (
            <div className="simulation-console">
              <div className="page-header">
                <h2>Adversarial Simulator</h2>
                <p>Target Subject: {selectedPersona.name}</p>
              </div>

              <div className="manual-input-box">
                <input 
                  type="text" 
                  placeholder="Custom Product Name" 
                  value={manualProduct} 
                  onChange={e => setManualProduct(e.target.value)} 
                />
                <input 
                  type="text" 
                  placeholder="Attributes (Optional)" 
                  value={manualAttrs} 
                  onChange={e => setManualAttrs(e.target.value)} 
                />
                <button onClick={handleManualSimulate}>Run Simulation</button>
              </div>

              {isStreamingComplete && (
                <ReviewDisplay 
                  simulation={simulation} 
                  persona={selectedPersona} 
                  dna={dna}
                />
              )}

              {(isSimLoading || simulation || simErrorStr) && (
                <NeuralPipeline 
                  simulation={simulation} 
                  isLoading={isSimLoading}
                  errorStr={simErrorStr}
                  onComplete={() => setIsStreamingComplete(true)}
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Business Mega Footer */}
      <footer className="business-footer">
        <div className="footer-col">
          <div className="brand-logo" style={{marginBottom: '16px'}}>
            <img src="/logo.svg" alt="Vorge Logo" />
            <h3>Vorge.</h3>
          </div>
          <p>Predictive Human Emulation for the Modern Enterprise.</p>
          <p className="copyright">&copy; 2026 Team Ziggiphase. All Rights Reserved.</p>
        </div>
        
        <div className="footer-col">
          <h4>Platform</h4>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab('home'); }}>Home</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab('pool'); }}>The Mind Pool</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab('taskB'); }}>Recommender</a>
          <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab('taskA'); }}>Simulator</a>
        </div>
        
        <div className="footer-col">
          <h4>Contact Us</h4>
          <p><strong>WhatsApp:</strong> +234 811 749 1902</p>
          <p><strong>Email:</strong> bellobasit790@gmail.com</p>
          <p><strong>Location:</strong> Lagos, Nigeria</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
