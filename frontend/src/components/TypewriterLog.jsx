import React, { useState, useEffect } from 'react';
import './TypewriterLog.css';

export default function TypewriterLog({ simulation, isLoading, errorStr }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (isLoading) {
      setDisplayedText('Initializing Neural Connection...\nLoading Contextual Embeddings...\nSynthesizing Behavior... \n');
      setIsTyping(true);
      return;
    }

    if (errorStr) {
      setDisplayedText((prev) => prev + `\n\n[ERROR]: ${errorStr}`);
      setIsTyping(false);
      return;
    }

    if (simulation && simulation.internal_monologue) {
      let fullText = `[PERSONA CORE ENGAGED]\n${simulation.internal_monologue}`;
      if (simulation.critique) {
        fullText += `\n\n[CONTEXTUAL AUDITOR]:\n${simulation.critique}`;
      }
      
      let currentIndex = 0;
      setDisplayedText('');
      setIsTyping(true);
      
      const intervalId = setInterval(() => {
        if (currentIndex < fullText.length) {
          // React state update using functional form to ensure we append correctly
          setDisplayedText((prev) => prev + fullText.charAt(currentIndex));
          currentIndex++;
        } else {
          clearInterval(intervalId);
          setIsTyping(false);
        }
      }, 15); // Adjust speed here (ms per char)

      return () => clearInterval(intervalId);
    }
  }, [simulation, isLoading, errorStr]);

  return (
    <div className="typewriter-container">
      <div className="terminal-header">
        <div className="window-controls">
          <span className="dot red"></span>
          <span className="dot yellow"></span>
          <span className="dot green"></span>
        </div>
        <span className="title">neural_synthesis.exe</span>
      </div>
      <div className="terminal-body">
        <pre className="typewriter-text">
          {displayedText}
          {isTyping && <span className="cursor-blink">█</span>}
        </pre>
      </div>
    </div>
  );
}
