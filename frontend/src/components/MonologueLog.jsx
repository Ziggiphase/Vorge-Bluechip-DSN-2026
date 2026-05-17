import React from 'react';
import './MonologueLog.css';

export default function MonologueLog({ simulation }) {
  if (!simulation) {
    return (
      <div className="log-empty">
        <div className="terminal-header">
          <span className="dot red"></span>
          <span className="dot yellow"></span>
          <span className="dot green"></span>
          <span className="title">adversarial_log.sh</span>
        </div>
        <div className="log-content empty">
          <p>Waiting for simulation...</p>
        </div>
      </div>
    );
  }

  const { internal_monologue, critique, fidelity } = simulation;

  return (
    <div className="log-container">
      <div className="terminal-header">
        <span className="dot red"></span>
        <span className="dot yellow"></span>
        <span className="dot green"></span>
        <span className="title">adversarial_workflow.sh</span>
      </div>
      
      <div className="log-content">
        <div className="log-entry stage-generator">
          <div className="entry-header">
            <span className="prompt">root@generator:~$</span>
            <span className="command">run_simulation --model qwen-32b</span>
          </div>
          <div className="entry-body monologue">
            <span className="label">[INTERNAL MONOLOGUE]:</span>
            <p>{internal_monologue}</p>
          </div>
        </div>

        <div className="log-entry stage-discriminator">
          <div className="entry-header">
            <span className="prompt">root@discriminator:~$</span>
            <span className="command">evaluate_fidelity --model llama-70b</span>
          </div>
          <div className="entry-body critique">
            <span className="label">[CRITIQUE]:</span>
            <p>{critique}</p>
          </div>
        </div>
        
        <div className="log-entry stage-result">
          <div className="entry-header">
            <span className="prompt">system@kernel:~$</span>
            <span className="command">finalize</span>
          </div>
          <div className="entry-body success">
            <p>✓ Simulation finalized with {(fidelity * 100).toFixed(2)}% synthetic confidence pass.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
