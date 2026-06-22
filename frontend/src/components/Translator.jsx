import { useCallback, useEffect, useRef, useState } from "react";
import { checkHealth, translateText } from "../api/translate";

const DEBOUNCE_MS = 500;

export default function Translator() {
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [sourceLang, setSourceLang] = useState("zh");
  const [targetLang, setTargetLang] = useState("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [latencyMs, setLatencyMs] = useState(null);
  const [serviceOk, setServiceOk] = useState(null);
  const debounceRef = useRef(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    checkHealth()
      .then(() => setServiceOk(true))
      .catch(() => setServiceOk(false));
  }, []);

  const doTranslate = useCallback(
    async (text, source, target) => {
      const trimmed = text.trim();
      if (!trimmed) {
        setOutputText("");
        setLatencyMs(null);
        setError("");
        return;
      }

      const requestId = ++requestIdRef.current;
      setLoading(true);
      setError("");

      try {
        const result = await translateText({
          text: trimmed,
          source,
          target,
        });

        if (requestId !== requestIdRef.current) return;

        setOutputText(result.translated_text);
        setLatencyMs(result.latency_ms);
      } catch (err) {
        if (requestId !== requestIdRef.current) return;
        setError(err.message || "翻译失败");
        setOutputText("");
        setLatencyMs(null);
      } finally {
        if (requestId === requestIdRef.current) {
          setLoading(false);
        }
      }
    },
    []
  );

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      doTranslate(inputText, sourceLang, targetLang);
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [inputText, sourceLang, targetLang, doTranslate]);

  const swapLanguages = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setInputText(outputText || inputText);
    setOutputText("");
  };

  const copyResult = async () => {
    if (!outputText) return;
    try {
      await navigator.clipboard.writeText(outputText);
    } catch {
      setError("复制失败，请手动选择文本复制");
    }
  };

  const clearAll = () => {
    setInputText("");
    setOutputText("");
    setError("");
    setLatencyMs(null);
  };

  return (
    <div className="translator">
      <div className="status-bar">
        <span className={`status-dot ${serviceOk === true ? "ok" : serviceOk === false ? "error" : ""}`} />
        <span>
          {serviceOk === null && "正在检测服务状态..."}
          {serviceOk === true && "翻译引擎已就绪"}
          {serviceOk === false && "翻译引擎未连接，请先启动 Docker 与后端服务"}
        </span>
        {latencyMs !== null && <span className="latency">响应 {latencyMs} ms</span>}
      </div>

      <div className="panels">
        <div className="panel">
          <div className="panel-header">
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              aria-label="源语言"
            >
              <option value="zh">中文</option>
              <option value="en">English</option>
            </select>
            <span className="char-count">{inputText.length} 字</span>
          </div>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="输入要翻译的文本，系统将自动翻译..."
            rows={10}
            maxLength={5000}
          />
        </div>

        <div className="panel-actions">
          <button type="button" className="icon-btn" onClick={swapLanguages} title="交换语言">
            ⇄
          </button>
        </div>

        <div className="panel">
          <div className="panel-header">
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              aria-label="目标语言"
            >
              <option value="en">English</option>
              <option value="zh">中文</option>
            </select>
            <div className="panel-tools">
              {loading && <span className="loading-text">翻译中...</span>}
              <button type="button" onClick={copyResult} disabled={!outputText}>
                复制
              </button>
              <button type="button" onClick={clearAll}>
                清空
              </button>
            </div>
          </div>
          <textarea
            value={outputText}
            readOnly
            placeholder="译文将显示在这里"
            rows={10}
          />
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
    </div>
  );
}
