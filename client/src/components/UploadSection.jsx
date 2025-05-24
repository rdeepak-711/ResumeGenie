import { useState } from "react";

function UploadSection() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const handleSubmit = () => {
    alert("Submitting to AI model soon!");
  };

  return (
    <section className="min-h-screen px-4 py-6 bg-white text-gray-800 flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-6 text-center">Try It Out</h2>

      <div className="w-full max-w-4xl flex flex-col md:flex-row gap-6">
        {/* Resume Input */}
        <div className="flex-1">
          <label className="block font-semibold mb-2">Paste your resume</label>
          <textarea
            rows="10"
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume text here..."
            className="w-full p-4 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none transition resize-none bg-gradient-to-br from-white to-indigo-50"
          />
        </div>

        {/* Job Description Input */}
        <div className="flex-1">
          <label className="block font-semibold mb-2">
            Paste Job Description
          </label>
          <textarea
            rows="10"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste job description here..."
            className="w-full p-4 border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none transition resize-none bg-gradient-to-br from-white to-indigo-50"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        className="mt-8 bg-indigo-700 text-white px-6 py-3 rounded-full hover:bg-indigo-800 transition font-semibold"
      >
        Analyze with AI
      </button>
    </section>
  );
}

export default UploadSection;
