import { FaInstagram, FaLinkedin } from "react-icons/fa";
import MusicPlayer from "./MusicPlayer";

export default function Footer({ playMusic }) {
  return (
    <footer className="w-full px-6 py-10 bg-gradient-to-br from-gray-900 to-black text-white backdrop-blur-md relative z-10">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 md:gap-0">
        {/* Logo and Tagline */}
        <div className="text-center md:text-left">
          <h3 className="text-2xl font-bold">Resume Genie</h3>
          <p className="text-sm text-indigo-200 mt-1">
            AI-Powered Job Matching
          </p>
        </div>

        {/* Social Links */}
        <div className="flex gap-6 text-xl">
          <a
            href="https://www.linkedin.com/company/code-philic/"
            target="_blank"
            rel="noopner noreferrer"
            className="hover:text-indigo-400 transition transform hover:scale-110"
          >
            <FaLinkedin />
          </a>
          <a
            href="https://www.instagram.com/code_philic/"
            target="_blank"
            rel="noopner noreferrer"
            className="hover:text-pink-400 transition transform hover:scale-110"
          >
            <FaInstagram />
          </a>
        </div>

        <MusicPlayer triggerPlay={playMusic} />
      </div>
      {/* Divider */}
      <div className="mt-6 border-t border-white/20 pt-4 text-center text-xs text-indigo-200">
        © {new Date().getFullYear()} Resume Genie. All rights reserved.
      </div>
    </footer>
  );
}
