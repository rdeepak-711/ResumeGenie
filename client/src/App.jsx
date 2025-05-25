import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";

export default function App() {
  return (
    <main className="h-screen w-screen overflow-y-scroll scroll-smooth snap-y snap-mandatory">
      <section className="snap-start h-screen">
        <Hero />
      </section>
      <section className="snap-start min-h-screen">
        <UploadSection />
      </section>
      <section className="snap-start min-h-[40vh]"></section>
    </main>
  );
}
