import { useState } from "react";
import { FaFilePdf, FaPaste, FaUpload } from "react-icons/fa";

function UploadSection() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [uploadMode, setUploadMode] = useState("paste");
  const [pdfFileName, setPdfFileName] = useState("");

  const handlePDFUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setPdfFileName(file.name);
      alert("PDF uploaded successfully!");
    } else {
      alert("Please upload a valid PDF file.");
      setPdfFileName("");
      e.target.value = null;
    }
  };

  const handleSubmit = () => {
    const totalLength = resumeText.length + jobDescription.length;
    if (totalLength > 1500) {
      alert("Total character count must be below 1500.");
      return;
    }
    alert("Analyzing with AI...");
  };

  return (
    <section className="min-h-screen flex flex-col justify-center items-center relative text-center px-6 bg-gradient-to-br from-gray-900 to-black text-white">
      <div className="bg-white/10 backdrop-blur-xl shadow-lg p-8 rounded-3xl w-full max-w-5xl">
        <h2 className="text-4xl font-extrabold text-center text-slate-300 mb-8 drop-shadow-md">
          Try Resume Genie
        </h2>

        <div className="grid md:grid-cols-2 gap-10">
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
                placeholder="Paste your resume text here..."
                className="w-full p-4 rounded-2xl text-sm bg-gray-900 border border-indigo-700 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-600 focus:outline-none transition-shadow duration-300 resize-none shadow-md"
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
              </div>
            )}
          </div>

          <div className="flex flex-col">
            <div className="mb-6 flex items-center min-h-[48px]">
              <label className="block font-semibold text-slate-400 text-center select-none text-xl ">
                Paste Job Description
              </label>
            </div>
            <textarea
              rows="10"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste your job description here..."
              className="w-full p-4 rounded-2xl text-sm bg-gray-900 border border-indigo-700 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-600 focus:outline-none transition-shadow duration-300 resize-none shadow-md"
              style={{ minHeight: "280px" }}
            />
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="mt-10 text-center">
        <button
          onClick={handleSubmit}
          className="bg-gradient-to-r from-indigo-700 to-slate-700 text-white px-10 py-3 rounded-full hover:scale-105 transition-transform duration-300 font-semibold shadow-xl drop-shadow-lg select-none"
          style={{ willChange: "transform" }}
        >
          Analyze with AI ✨
        </button>
      </div>
    </section>
  );
}

export default UploadSection;
