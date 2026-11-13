import { useState, useEffect } from "react";

import ChatWindow from "./components/ChatWindow";
import FileUpload from "./components/FileUpload";

import { checkHealth, uploadPDF, sendMessage } from "./services/api";

import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [error, setError] = useState("");

  // Check backend connection
  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Disconnected"));
  }, []);

  // Handle PDF upload
  const handleUpload = async (file) => {
    setError("");
    setUploadResult(null);

    if (file.type !== "application/pdf") {
      setError("Please select a valid PDF file.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("PDF size must not exceed 20 MB.");
      return;
    }

    setUploading(true);

    try {
      const result = await uploadPDF(file);
      setUploadResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // Handle user questions
  const handleSend = async (question) => {
    setError("");

    setMessages((previous) => [
      ...previous,
      { role: "user", content: question },
    ]);

    setLoading(true);

    try {
      const result = await sendMessage(question);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Enterprise AI Knowledge Assistant</h1>
          <p>Ask questions. Get answers from your documents.</p>
        </div>

        <div className="backend-status">
          <span
            className={
              backendStatus === "Connected" ? "status-dot online" : "status-dot"
            }
          />
          Backend: {backendStatus}
        </div>
      </header>

      <main className="app-main">
        <section className="document-panel">
          <h2>Knowledge Base</h2>
          <p>Upload a PDF document to get started.</p>

          <FileUpload
            onUpload={handleUpload}
            uploading={uploading}
            uploadResult={uploadResult}
          />

          {error && <div className="error-message">{error}</div>}
        </section>

        <section className="chat-panel">
          <ChatWindow
            messages={messages}
            onSend={handleSend}
            loading={loading}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
