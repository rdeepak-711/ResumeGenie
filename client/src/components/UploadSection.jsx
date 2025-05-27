import { useState } from "react";
import { FaFilePdf, FaPaste, FaUpload, FaSpinner } from "react-icons/fa";

function UploadSection({ setPlayMusic }) {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [uploadMode, setUploadMode] = useState("paste");
  const [pdfFileName, setPdfFileName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const FREE_LIMITS = {
    resume_chars: 1000,
    jd_chars: 1500,
    total_chars: 2500,
  };

  const convertToLatex = (plainText) => {
    if (!plainText.trim()) return "";

    const latexTemplate = `\\documentclass[letterpaper,11pt]{article}
      \\usepackage{latexsym}
      \\usepackage[empty]{fullpage}
      \\usepackage{titlesec}
      \\usepackage{marvosym}
      \\usepackage[usenames,dvipsnames]{color}
      \\usepackage{verbatim}
      \\usepackage{enumitem}
      \\usepackage[hidelinks]{hyperref}
      \\usepackage{fancyhdr}
      \\usepackage[english]{babel}
      \\usepackage{tabularx}

      \\begin{document}

      ${plainText
        .split("\n")
        .map((line) => {
          if (line.trim() === "") return "";
          // Simple formatting - you can enhance this logic
          if (
            line.trim().length < 50 &&
            !line.includes("@") &&
            !line.includes("•")
          ) {
            return `\\section{${line.trim()}}`;
          }
          return line.trim();
        })
        .join("\n\n")}

      \\end{document}`;

    return latexTemplate;
  };

  const extractTextFromPDF = async (file) => {
    try {
      const pdfjsLib = await import("pdfjs-dist/legacy/build/pdf");
      const pdfjsWorker = await import("pdfjs-dist/legacy/build/pdf.worker");

      pdfjsLib.GlobalWorkerOptions.workerSrc = window.URL.createObjectURL(
        new Blob([`importScripts("${pdfjsWorker}")`], {
          type: "application/javascript",
        })
      );
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

      let fullText = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item) => item.str).join(" ");
        fullText += pageText + "\n";
      }

      return fullText.trim();
    } catch (error) {
      console.error("PDF extraction error:", error);
      throw new Error(
        "Failed to extract text from PDF. Please try pasting text instead."
      );
    }
  };

  const handlePDFUpload = async (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setPdfFileName(file.name);
      setError("");

      try {
        setIsLoading(true);
        const extractedText = await extractTextFromPDF(file);
        setResumeText(extractedText);
        setIsLoading(false);
      } catch (err) {
        setError(err.message);
        setPdfFileName("");
        e.target.value = null;
        setIsLoading(false);
      }
    } else {
      alert("Please upload a valid PDF file.");
      setPdfFileName("");
      e.target.value = null;
    }
  };

  const checkLimits = () => {
    const resumeChars = resumeText.length;
    const jdChars = jobDescription.length;
    const totalChars = resumeChars + jdChars;

    const errors = [];
    if (resumeChars > FREE_LIMITS.resume_chars) {
      errors.push(
        `Resume too long: ${resumeChars}/${FREE_LIMITS.resume_chars} characters`
      );
    }
    if (jdChars > FREE_LIMITS.jd_chars) {
      errors.push(
        `Job description too long: ${jdChars}/${FREE_LIMITS.jd_chars} characters`
      );
    }
    if (totalChars > FREE_LIMITS.total_chars) {
      errors.push(
        `Total content too long: ${totalChars}/${FREE_LIMITS.total_chars} characters`
      );
    }

    return {
      valid: errors.length === 0,
      errors,
      current: { resumeChars, jdChars, totalChars },
    };
  };

  const BACKEND_API = import.meta.env.VITE_BACKEND_API;

  const analyzeResume = async () => {
    try {
      console.log("Backend API endpoint:", BACKEND_API);
      setIsLoading(true);
      setError("");
      setAnalysisResult(null);

      const latexResume = resumeText.includes("\\documentclass")
        ? resumeText
        : convertToLatex(resumeText);

      const response = await fetch(`${BACKEND_API}/resume/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume: latexResume,
          jobDescription,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setAnalysisResult(data.result);
        setPlayMusic(false);
      } else {
        setError(data.message || "An error occurred during analysis.");
      }
    } catch (err) {
      console.error("Analysis error:", err);
      setError("Failed to analyze resume. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError("Please provide both resume and job description");
      return;
    }

    const limitCheck = checkLimits();
    if (!limitCheck.valid) {
      setError(limitCheck.errors.join(". "));
      return;
    }
    setPlayMusic(true);
    setError("");
    analyzeResume();
  };

  const limitCheck = checkLimits();

  return (
    <section className="flex-1 flex flex-col justify-start items-center text-center px-4 py-12 bg-gradient-to-br from-gray-900 to-black text-white">
      <div className="bg-white/10 backdrop-blur-lg shadow-2xl p-6 sm:p-10 rounded-3xl w-full max-w-5xl">
        <h2 className="text-4xl font-extrabold text-center text-slate-300 mb-8 drop-shadow-md">
          Try Resume Genie
        </h2>

        {/* Character Count Display */}
        <div className="mb-6 text-center">
          <div
            className={`text-sm ${
              limitCheck.valid ? "text-slate-400" : "text-red-400"
            }`}
          >
            Resume: {limitCheck.current.resumeChars}/{FREE_LIMITS.resume_chars}{" "}
            | Job Description: {limitCheck.current.jdChars}/
            {FREE_LIMITS.jd_chars} | Total: {limitCheck.current.totalChars}/
            {FREE_LIMITS.total_chars}
          </div>
          {!limitCheck.valid && (
            <div className="text-red-400 text-sm mt-2">
              Free tier limits exceeded. Sign up for more characters!
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {/* Resume Input Section */}
          <div className="flex flex-col">
            <div className="flex gap-4 mb-6 justify-center md:justify-start items-center min-h-[48px]">
              <button
                onClick={() => {
                  setUploadMode("paste");
                  setPdfFileName("");
                }}
                className={`flex items-center gap-2 px-5 py-2 rounded-full transition font-semibold text-sm md:text-base ${
                  uploadMode === "paste"
                    ? "bg-indigo-700 text-white shadow-lg"
                    : "bg-transparent text-slate-400 border border-slate-600 hover:bg-indigo-700 hover:text-white"
                }`}
                style={{ willChange: "transform, background-color" }}
              >
                <FaPaste />
                Paste Text
              </button>
              <button
                onClick={() => {
                  setUploadMode("upload");
                  setResumeText("");
                }}
                className={`flex items-center gap-2 px-5 py-2 rounded-full transition font-semibold text-sm md:text-base ${
                  uploadMode === "upload"
                    ? "bg-indigo-700 text-white shadow-lg"
                    : "bg-transparent text-slate-400 border border-slate-600 hover:bg-indigo-700 hover:text-white"
                }`}
                style={{ willChange: "transform, background-color" }}
              >
                <FaFilePdf />
                Upload PDF
              </button>
            </div>

            {uploadMode === "paste" ? (
              <textarea
                rows="10"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here (plain text or LaTeX)..."
                className={`w-full p-4 rounded-2xl text-sm bg-gray-900 border text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-600 focus:outline-none transition-shadow duration-300 resize-none shadow-md ${
                  limitCheck.current.resumeChars > FREE_LIMITS.resume_chars
                    ? "border-red-500"
                    : "border-indigo-700"
                }`}
                style={{ minHeight: "280px" }}
              />
            ) : (
              <div className="flex flex-col items-center md:items-start gap-3">
                <label
                  htmlFor="pdfUpload"
                  className="cursor-pointer inline-flex items-center gap-2 bg-indigo-700 hover:bg-indigo-800 text-white px-6 py-3 rounded-2xl transition-transform duration-200 font-semibold shadow-lg hover:scale-105"
                  title="Upload PDF"
                >
                  <FaUpload />
                  {pdfFileName ? "Change PDF" : "Choose PDF"}
                </label>
                <input
                  type="file"
                  id="pdfUpload"
                  accept="application/pdf"
                  onChange={handlePDFUpload}
                  className="hidden"
                />
                {pdfFileName && (
                  <p className="text-indigo-400 text-sm truncate max-w-xs text-center md:text-left drop-shadow-sm">
                    {pdfFileName}
                  </p>
                )}
                {resumeText && uploadMode === "upload" && (
                  <div className="mt-4 p-3 bg-gray-800 rounded-lg max-h-40 overflow-y-auto text-xs text-slate-300">
                    <p className="font-semibold mb-2">
                      Extracted Text Preview:
                    </p>
                    <p className="whitespace-pre-wrap">
                      {resumeText.substring(0, 200)}...
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Job Description Section */}
          <div className="flex flex-col">
            <div className="mb-6 flex items-center min-h-[48px]">
              <label className="block font-semibold text-slate-400 text-center select-none text-xl">
                Paste Job Description
              </label>
            </div>
            <textarea
              rows="10"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste your job description here..."
              className={`w-full p-4 rounded-2xl text-sm bg-gray-900 border text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-600 focus:outline-none transition-shadow duration-300 resize-none shadow-md ${
                limitCheck.current.jdChars > FREE_LIMITS.jd_chars
                  ? "border-red-500"
                  : "border-indigo-700"
              }`}
              style={{ minHeight: "280px" }}
            />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Analysis Result */}
        {analysisResult && (
          <div className="mt-8 p-6 bg-green-900/20 border border-green-500 rounded-lg text-left">
            <h3 className="text-xl font-bold text-green-400 mb-4">
              Analysis Complete! Score: {analysisResult.score}/100
            </h3>

            <div className="mb-4">
              <h4 className="font-semibold text-slate-300 mb-2">Feedback:</h4>
              <p className="text-slate-400 text-sm">
                {analysisResult.feedback}
              </p>
            </div>

            <div className="mb-4">
              <h4 className="font-semibold text-slate-300 mb-2">
                Optimized Resume (LaTeX):
              </h4>
              <div className="bg-gray-800 p-3 rounded max-h-60 overflow-y-auto">
                <pre className="text-xs text-slate-300 whitespace-pre-wrap">
                  {analysisResult.tailored_resume}
                </pre>
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={() =>
                  navigator.clipboard.writeText(analysisResult.tailored_resume)
                }
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
              >
                Copy LaTeX Code
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="mt-10 mb-2">
        <button
          onClick={handleSubmit}
          disabled={
            isLoading ||
            !limitCheck.valid ||
            !resumeText.trim() ||
            !jobDescription.trim()
          }
          className={`px-8 py-3 rounded-full font-semibold shadow-xl transition-all ${
            isLoading ||
            !limitCheck.valid ||
            !resumeText.trim() ||
            !jobDescription.trim()
              ? "bg-gray-600 text-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:scale-105"
          }`}
          style={{ willChange: "transform" }}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <FaSpinner className="animate-spin" />
              Analyzing...
            </span>
          ) : (
            "Analyze with AI ✨"
          )}
        </button>
      </div>

      {/* Sign up prompt for over-limit users */}
      {!limitCheck.valid && (
        <div className="mt-4 text-center">
          <p className="text-slate-400 text-sm mb-2">
            Need more characters? Sign up for a free account!
          </p>
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-full transition">
            Sign Up for Free Credits
          </button>
        </div>
      )}
    </section>
  );
}

export default UploadSection;
