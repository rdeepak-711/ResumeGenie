import { useState } from "react";
import Footer from "./components/Footer";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";

export default function App() {
  const [playMusic, setPlayMusic] = useState(false);

  return (
    <main className="h-screen w-screen overflow-y-scroll scroll-smooth snap-y snap-mandatory">
      <section className="snap-start h-screen">
        <Hero />
      </section>
      <section className="snap-start h-screen flex flex-col">
        <UploadSection setPlayMusic={setPlayMusic} />
        <Footer playMusic={playMusic} />
      </section>
    </main>
  );
}
