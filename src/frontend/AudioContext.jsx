import React, { createContext, useContext, useRef, useState } from 'react';

const AudioContext = createContext();

export const AudioProvider = ({ children }) => {
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef(null);

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !audioRef.current.muted;
      setIsMuted(!isMuted);
    }
  };

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(error => console.error('Playback failed', error));
    }
  };

  return (
    <AudioContext.Provider value={{ isMuted, toggleMute, playAudio }}>
      <audio ref={audioRef} src="/In The Air.mp3" style={{ display: 'none' }}></audio>
      {children}
    </AudioContext.Provider>
  );
};

export const useAudio = () => {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
}; 