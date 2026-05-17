import React, { useState, useEffect } from 'react';
import './NeuralPipeline.css';

export default function NeuralPipeline({ simulation, isLoading, errorStr, onComplete }) {
  const [stage, setStage] = useState(0); // 0=init, 1=actor, 2=auditor, 3=director, 4=done
  const [actorText, setActorText] = useState('');
  const [auditorText, setAuditorText] = useState('');
  const [directorText, setDirectorText] = useState('');

  useEffect(() => {
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
      let currentStage = 1;
      setStage(1);
      
      const streamText = (textToStream, setter, onFinish) => {
        let i = 0;
        const interval = setInterval(() => {
          if (i < textToStream.length) {
            setter(prev => prev + textToStream.charAt(i));
            i++;
          } else {
            clearInterval(interval);
            onFinish();
          }
        }, 10);
      };

      // Stage 1: The Actor
      streamText(simulation.generator_log, setActorText, () => {
        setStage(2);
        
        // Stage 2: The Auditor
        if (simulation.discriminator_log) {
          streamText(simulation.discriminator_log, setAuditorText, () => {
            setStage(3);
            
            // Stage 3: The Director
            if (simulation.refiner_log) {
              streamText(simulation.refiner_log, setDirectorText, () => {
                setStage(4);
                if (onComplete) onComplete();
              });
            } else {
              setStage(4);
              if (onComplete) onComplete();
            }
          });
        } else {
          setStage(4);
          if (onComplete) onComplete();
        }
      });
    }
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
