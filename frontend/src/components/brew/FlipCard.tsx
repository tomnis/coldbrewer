import React from "react";

export default function FlipCard({ isFlipped, front, back }: { isFlipped: boolean; front: React.ReactNode; back: React.ReactNode }) {
  return (
    <div className="flip-card-container">
      <div className={`flip-card ${isFlipped ? "flipped" : ""}`}>
        <div className="flip-card-front">{front}</div>
        <div className="flip-card-back">{back}</div>
      </div>
    </div>
  );
}
