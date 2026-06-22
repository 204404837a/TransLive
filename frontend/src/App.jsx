import Translator from "./components/Translator";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>TransLive 智译通</h1>
          <p>基于开源神经机器翻译的实时中英互译系统</p>
        </div>
      </header>
      <main>
        <Translator />
      </main>
      <footer className="app-footer">
        <span>Powered by LibreTranslate · FastAPI · React</span>
      </footer>
    </div>
  );
}
