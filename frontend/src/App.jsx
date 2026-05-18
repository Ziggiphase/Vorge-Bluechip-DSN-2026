import React, { useState, useEffect } from 'react';
import PersonaCard from './components/PersonaCard';
import RecommendationEngine from './components/RecommendationEngine';
import NeuralPipeline from './components/NeuralPipeline';
import ReviewDisplay from './components/ReviewDisplay';
import './App.css';

const API_BASE = '/api';

function App() {
  const [activeTab, setActiveTab] = useState('pool'); // pool, taskB, taskA
  const [personas, setPersonas] = useState([]);
  
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
  
  // API Key Persistence
  const [apiKey, setApiKey] = useState(localStorage.getItem('groq_api_key') || '');
  const [showApiModal, setShowApiModal] = useState(!localStorage.getItem('groq_api_key'));
  
  useEffect(() => {
    fetch(`${API_BASE}/users?limit=500`)
      .then(res => res.json())
      .then(data => setPersonas(data.users || []))
      .catch(err => console.error("Failed to fetch users", err));
  }, []);

  const saveApiKey = () => {
    if (apiKey) {
      localStorage.setItem('groq_api_key', apiKey);
      setShowApiModal(false);
    }
  };

  const skipApiKey = () => {
    setShowApiModal(false);
  };

  const handleSelectPersona = async (p) => {
    setSelectedPersona(p);
    
    // Reset Task A Col
    setSimulation(null);
    setDna(null);
    setSimErrorStr('');
    setIsStreamingComplete(false);

    // Trigger Task B (Recommendations)
    if (!apiKey) return;
    
    setIsRecLoading(true);
    setRecommendations([]);
    setRecErrorStr('');
    
    try {
      const response = await fetch(`${API_BASE}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: p.user_id, api_key: apiKey || '' })
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
          api_key: apiKey || ''
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
    
    if (activeFilter === 'Elite') return p.is_elite;
    if (activeFilter === 'Harsh') return parseFloat(p.avg_stars) < 3.0;
    if (activeFilter === 'Optimist') return parseFloat(p.avg_stars) >= 4.0;
    return true; // 'All'
  });

  return (
    <div className="app-container">
      {showApiModal && (
        <div className="api-modal-overlay">
          <div className="api-modal">
            <h2>Welcome to Vorge</h2>
            <p>To use the Neural Pipeline, please enter your Groq API Key.</p>
            <input 
              type="password" 
              placeholder="gsk_..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <div style={{display: 'flex', gap: '10px'}}>
              <button onClick={saveApiKey} style={{flex: 1}}>Save & Start</button>
              <button onClick={skipApiKey} style={{background: 'transparent', border: '1px solid #555', color: '#fff'}}>Skip (Use Server Key)</button>
            </div>
          </div>
        </div>
      )}

      <div className="top-nav">
        <h1>Vorge</h1>
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'pool' ? 'active' : ''}`}
            onClick={() => setActiveTab('pool')}
          >
            The Mind Pool
          </button>
          <button 
            className={`nav-tab ${activeTab === 'taskB' ? 'active' : ''}`}
            onClick={() => setActiveTab('taskB')}
          >
            Task B: Recommender
          </button>
          <button 
            className={`nav-tab ${activeTab === 'taskA' ? 'active' : ''}`}
            onClick={() => setActiveTab('taskA')}
          >
            Task A: Simulator
          </button>
        </div>
      </div>

      {activeTab === 'pool' && (
        <div className="page-view">
          <div className="page-header">
            <h2>The Mind Pool</h2>
            <p>Select a persona to trigger cross-domain recommendations.</p>
          </div>
          
          <div className="pool-controls">
            <input 
              type="text" 
              placeholder="Search 500 profiles..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="filter-pills">
              {['All', 'Elite', 'Harsh', 'Optimist'].map(f => (
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
              <div 
                key={p.user_id} 
                className={selectedPersona?.user_id === p.user_id ? 'persona-wrapper selected' : 'persona-wrapper'}
                onClick={() => handleSelectPersona(p)}
              >
                <PersonaCard persona={p} onClick={() => {}} />
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'taskB' && (
        <div className="page-view">
          {!selectedPersona ? (
            <div className="empty-tab-state">
              <span className="icon">🎯</span>
              <h2>No Persona Selected</h2>
              <p>Please select a Persona from the Mind Pool first to generate recommendations.</p>
              <button className="btn-goto-pool" onClick={() => setActiveTab('pool')}>Go to Mind Pool</button>
            </div>
          ) : (
            <RecommendationEngine 
              persona={selectedPersona}
              recommendations={recommendations}
              isLoading={isRecLoading}
              errorStr={recErrorStr}
              onSimulate={triggerSimulation}
            />
          )}
        </div>
      )}

      {activeTab === 'taskA' && (
        <div className="page-view" style={{maxWidth: '800px'}}>
          {!selectedPersona ? (
            <div className="empty-tab-state">
              <span className="icon">🧪</span>
              <h2>Simulation Console Offline</h2>
              <p>Please select a Persona from the Mind Pool first to run the simulation.</p>
              <button className="btn-goto-pool" onClick={() => setActiveTab('pool')}>Go to Mind Pool</button>
            </div>
          ) : (
            <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
              <div className="page-header" style={{marginBottom: '0'}}>
                <h2>Adversarial Simulation</h2>
                <p>Target Persona: <strong>{selectedPersona.name}</strong></p>
              </div>

              <div className="manual-input-box">
                <input 
                  placeholder="Test a custom product name..." 
                  value={manualProduct}
                  onChange={(e) => setManualProduct(e.target.value)}
                />
                <input 
                  placeholder="Attributes (Optional)" 
                  value={manualAttrs}
                  onChange={(e) => setManualAttrs(e.target.value)}
                />
                <button onClick={handleManualSimulate}>Run</button>
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
    </div>
  );
}

export default App;
