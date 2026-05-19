import React, { useState, useEffect } from 'react';
import './NeuralPipeline.css';

export default function NeuralPipeline({ simulation, isLoading, errorStr, onComplete }) {
  const [stage, setStage] = useState(0); // 0=init, 1=actor, 2=auditor, 3=director, 4=done
  const [actorText, setActorText] = useState('');
  const [auditorText, setAuditorText] = useState('');
  const [directorText, setDirectorText] = useState('');

  useEffect(() => {
    let timeouts = [];
    if (isLoading) {
      setStage(0);
      setActorText('');
      setAuditorText('');
      setDirectorText('');
      return;
    }

    if (errorStr) {
      setStage(0);
      return;
    }

    if (simulation && simulation.generator_log) {
      setStage(1);
      
      const streamText = (text, setter, onFinish, delayOffset = 0) => {
        for (let i = 0; i <= text.length; i++) {
          const timeoutId = setTimeout(() => {
            setter(text.slice(0, i));
            if (i === text.length) {
              onFinish();
            }
          }, delayOffset + i * 15);
          timeouts.push(timeoutId);
        }
        return delayOffset + text.length * 15;
      };

      // Stage 1: The Actor
      let time = streamText(simulation.generator_log, setActorText, () => setStage(2), 0);
      
      // Stage 2: The Auditor
      if (simulation.discriminator_log) {
        time = streamText(simulation.discriminator_log, setAuditorText, () => setStage(3), time + 300);
        
        // Stage 3: The Director
        if (simulation.refiner_log) {
          streamText(simulation.refiner_log, setDirectorText, () => {
            setStage(4);
            if (onComplete) onComplete();
          }, time + 300);
        } else {
          const t = setTimeout(() => { setStage(4); if (onComplete) onComplete(); }, time + 300);
          timeouts.push(t);
        }
      } else {
        const t = setTimeout(() => { setStage(4); if (onComplete) onComplete(); }, time + 300);
        timeouts.push(t);
      }
    }
    
    return () => timeouts.forEach(clearTimeout);
  }, [simulation, isLoading, errorStr]);

  return (
    <div className="pipeline-container">
      <div className="pipeline-header">
        <div className="window-controls">
          <span className="dot red"></span><span className="dot yellow"></span><span className="dot green"></span>
        </div>
        <span className="title">Vorge</span>
      </div>

      <div className="pipeline-body">
        {isLoading && (
          <div className="pipeline-node loading">
            <span className="node-icon blink">⚡</span>
            <p>Initializing Deep Behavioral Synthesis...</p>
          </div>
        )}

        {errorStr && (
          <div className="pipeline-node error">
            <span className="node-icon">❌</span>
            <p>{errorStr}</p>
          </div>
        )}

        {(stage > 0 || actorText) && (
          <div className={`pipeline-node ${stage === 1 ? 'active' : 'done'}`}>
            <div className="node-header">
              <span className="node-icon">🎭</span>
              <h4>Stage 1: The Actor (Generator)</h4>
            </div>
            <pre className="node-output">{actorText}{stage === 1 && <span className="cursor">█</span>}</pre>
          </div>
        )}

        {(stage > 1 || auditorText) && (
          <div className={`pipeline-node ${stage === 2 ? 'active' : 'done'}`}>
            <div className="node-header">
              <span className="node-icon">⚖️</span>
              <h4>Stage 2: Contextual Auditor (Discriminator)</h4>
            </div>
            <pre className="node-output">{auditorText}{stage === 2 && <span className="cursor">█</span>}</pre>
          </div>
        )}

        {(stage > 2 || directorText) && (
          <div className={`pipeline-node ${stage === 3 ? 'active' : 'done'}`}>
            <div className="node-header">
              <span className="node-icon">🎬</span>
              <h4>Stage 3: The Director (Refiner)</h4>
            </div>
            <pre className="node-output">{directorText}{stage === 3 && <span className="cursor">█</span>}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
