import { useEffect, useState } from "react";

const phrases = [
  "Tailor your resume with AI.",
  "Upload your resume & match it with jobs.",
  "Get instant insights to stand out.",
];

function Hero() {
  const [displayedText, setDisplayedText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    let timeout;

    if (isTyping) {
      if (charIndex < phrases[phraseIndex].length) {
        timeout = setTimeout(() => {
          setDisplayedText((prev) => prev + phrases[phraseIndex][charIndex]);
          setCharIndex(charIndex + 1);
        }, 80);
        return () => clearTimeout(timeout);
      } else {
        timeout = setTimeout(() => {
          setIsTyping(false);
        }, 1500);
      }
    } else {
      if (charIndex > 0) {
        timeout = setTimeout(() => {
          setDisplayedText((prev) => prev.slice(0, -1));
          setCharIndex((prev) => prev - 1);
        }, 40);
      } else {
        setPhraseIndex((prev) => (prev + 1) % phrases.length);
        setIsTyping(true);
      }
    }
    return () => clearTimeout(timeout);
  }, [charIndex, isTyping, phraseIndex]);

  return (
    <section className="h-screen flex flex-col justify-center items-center relative text-center px-6 bg-gradient-to-br from-gray-900 to-black text-white">
      <h1 className="text-4xl md:text-6xl font-bold mb-4">Resume Genie</h1>
      <p className="text-indigo-300 text-lg md:text-xl max-w-xl mb-8 font-mono min-h-[2rem]">
        {displayedText}
        <span className="border-r-2 border-indigo-300 animate-pulse ml-1" />
      </p>
      <div className="flex gap-4">
        <button className="bg-white text-indigo-700 px-6 py-2 rounded-full font-semibold hover:bg-gray-300 transition">
          Login
        </button>
        <button className="bg-transparent border-2 border-white px-6 py-2 rounded-full font-semibold hover:bg-white hover:text-indigo-700 transition">
          Signup
        </button>
      </div>

      {/* Scroll instruction */}
      <p className="absolute bottom-20 text-sm text-indigo-300 animate-pulse">
        Scroll down to try it out 👇
      </p>
      <button
        onClick={() =>
          window.scrollBy({ top: window.innerHeight, behavior: "smooth" })
        }
        className="absolute bottom-10 animate-bounce text-indigo-300 hover:text-indigo-100 transition text-3xl"
      >
        ↓
      </button>
    </section>
  );
}

export default Hero;
