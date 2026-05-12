// Younds bear — sleepy forest adventurer.
// Built from circles + ellipses only (no complex paths) so it stays "intentionally simple".

function YoundsBear({ size = 120, mood = "sleepy", style }) {
  // mood: "sleepy" (default), "happy" (download done), "curious" (searching)
  const eyeOpenY = mood === "sleepy" ? 0.55 : 0.0;
  const eyeOpenH = mood === "sleepy" ? 0.45 : 1.0;
  const mouthCurve = mood === "happy" ? 8 : mood === "curious" ? -2 : 2;

  return (
    <svg
      viewBox="0 0 200 200"
      width={size}
      height={size}
      style={{ display: "block", ...style }}
      aria-label="Younds bear mascot"
    >
      {/* shadow under bear */}
      <ellipse cx="100" cy="180" rx="62" ry="6" fill="rgba(58,40,24,.18)" />

      {/* body */}
      <ellipse cx="100" cy="138" rx="58" ry="44" fill="#a07050" />
      <ellipse cx="100" cy="146" rx="42" ry="30" fill="#c89976" />

      {/* left ear */}
      <circle cx="48" cy="60" r="20" fill="#8b5e3c" />
      <circle cx="48" cy="60" r="10" fill="#d4a888" />
      {/* right ear */}
      <circle cx="152" cy="60" r="20" fill="#8b5e3c" />
      <circle cx="152" cy="60" r="10" fill="#d4a888" />

      {/* head */}
      <circle cx="100" cy="84" r="58" fill="#a07050" />

      {/* cheeks (warm blush) */}
      <ellipse cx="58" cy="100" rx="10" ry="6" fill="#e8a888" opacity="0.55" />
      <ellipse cx="142" cy="100" rx="10" ry="6" fill="#e8a888" opacity="0.55" />

      {/* snout */}
      <ellipse cx="100" cy="104" rx="28" ry="22" fill="#e8c8a8" />

      {/* nose */}
      <ellipse cx="100" cy="92" rx="7" ry="5" fill="#3a2818" />

      {/* mouth — small curve made from two short ellipses */}
      <ellipse
        cx="100"
        cy={108 + mouthCurve}
        rx="8"
        ry={Math.abs(mouthCurve) + 1.5}
        fill="none"
        stroke="#3a2818"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* eyes — sleepy = lower half of the circle visible */}
      {/* left */}
      <g transform="translate(72,78)">
        <circle r="6" fill="#3a2818" opacity={mood === "sleepy" ? 0 : 1} />
        {/* sleepy eyelid: a horizontal line + small lash arc */}
        {mood === "sleepy" && (
          <>
            <ellipse cx="0" cy="2" rx="7" ry="4" fill="#3a2818" />
            <ellipse cx="0" cy="-1" rx="8" ry="4" fill="#a07050" />
          </>
        )}
      </g>
      {/* right */}
      <g transform="translate(128,78)">
        <circle r="6" fill="#3a2818" opacity={mood === "sleepy" ? 0 : 1} />
        {mood === "sleepy" && (
          <>
            <ellipse cx="0" cy="2" rx="7" ry="4" fill="#3a2818" />
            <ellipse cx="0" cy="-1" rx="8" ry="4" fill="#a07050" />
          </>
        )}
      </g>

      {/* tiny scarf — forest-green, just a few rectangles/ellipses */}
      <ellipse cx="100" cy="130" rx="48" ry="9" fill="#3d5c3a" />
      <ellipse cx="100" cy="129" rx="48" ry="4" fill="#4d7048" />
      <ellipse cx="138" cy="135" rx="6" ry="10" fill="#3d5c3a" />

      {/* paws */}
      <circle cx="58" cy="170" r="14" fill="#8b5e3c" />
      <circle cx="142" cy="170" r="14" fill="#8b5e3c" />
      <circle cx="58" cy="172" r="6" fill="#d4a888" />
      <circle cx="142" cy="172" r="6" fill="#d4a888" />

      {/* sleepy "z" floating up — only when sleepy */}
      {mood === "sleepy" && (
        <g opacity="0.6" style={{ animation: "youndsZzz 3s ease-in-out infinite" }}>
          <text x="172" y="40" fontFamily="Newsreader, serif" fontSize="14" fill="#3a2818" fontStyle="italic">z</text>
          <text x="184" y="28" fontFamily="Newsreader, serif" fontSize="11" fill="#3a2818" fontStyle="italic">z</text>
        </g>
      )}
    </svg>
  );
}

// Tiny brand logomark — just the bear silhouette in a rounded square
function YoundsLogo({ size = 28 }) {
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} style={{ display: "block" }}>
      <rect x="0" y="0" width="64" height="64" rx="14" fill="#3d5c3a" />
      <circle cx="20" cy="22" r="7" fill="#d4a888" />
      <circle cx="44" cy="22" r="7" fill="#d4a888" />
      <circle cx="32" cy="34" r="18" fill="#d4a888" />
      <ellipse cx="32" cy="40" rx="9" ry="7" fill="#f5ecd9" />
      <ellipse cx="32" cy="36" rx="2.5" ry="1.8" fill="#3a2818" />
      <circle cx="26" cy="32" r="1.6" fill="#3a2818" />
      <circle cx="38" cy="32" r="1.6" fill="#3a2818" />
    </svg>
  );
}

Object.assign(window, { YoundsBear, YoundsLogo });
