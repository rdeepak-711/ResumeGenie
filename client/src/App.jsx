import { useRef } from "react";

import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";

export default function App() {
  const uploadRef = useRef(null);

  const handleScroll = () => {
    uploadRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  return (
    <>
      <Hero onScrollClick={handleScroll} />
      <div ref={uploadRef}>
        <UploadSection />
      </div>
    </>
  );
}
