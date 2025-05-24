import { useEffect, useState } from "react";

const phrases = [
  "Upload your resume, get insights.",
  "Match your resume with the job.",
  "Improve your chances with AI.",
];

export default function Hero({ onScrollClick }) {
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    const currentMessage = phrases[currentTextIndex];

    if (charIndex < currentMessage.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + currentMessage[charIndex]);
        setCharIndex((prev) => prev + 1);
      }, 50);
      return () => clearTimeout(timeout);
    } else {
      const pause = setTimeout(() => {
        setDisplayedText("");
        setCharIndex(0);
        setCurrentTextIndex((prev) => (prev + 1) % phrases.length);
      }, 2000);
      return () => clearTimeout(pause);
    }
  }, [charIndex, currentTextIndex, phrases]);

  return (
    <section className="h-screen w-screen overflow-hidden flex flex-col justify-center items-center relative text-center px-6 bg-gradient-to-br from-[#1e1b4b] to-[#111827] text-white">
      <h1 className="text-4xl md:text-6xl font-bold mb-4">Resume Genie</h1>

      <p className="text-indigo-200 text-lg md:text-xl max-w-xl mb-8 transition-all duration-500 ease-in-out">
        {displayedText}
        <span className="inline-block w-[1px] h-[1.2em] bg-white animate-blink ml-1"></span>
      </p>
      <div className="flex gap-4">
        <button className="bg-white text-indigo-700 px-6 py-2 rounded-full font-semibold hover:bg-gray-300 transition">
          Login
        </button>
        <button className="bg-transparent border-2 border-white px-6 py-2 rounded-full font-semibold hover:bg-white hover:text-indigo-700 transition">
          Signup
        </button>
      </div>

      {/* Scroll down button */}
      <button
        onClick={onScrollClick}
        className="absolute bottom-10 animate-bounce text-indigo-300 hover:text-indigo-100 transition"
      >
        ↓ Scroll to try
      </button>
    </section>
  );
}
