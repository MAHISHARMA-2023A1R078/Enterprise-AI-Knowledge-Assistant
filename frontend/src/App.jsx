import { useState, useEffect } from "react";

import ChatWindow from "./components/ChatWindow";
import FileUpload from "./components/FileUpload";

import {
  checkHealth,
  uploadPDF,
  sendMessage,
  deleteDocument,
} from "./services/api";

import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [error, setError] = useState("");
  const [activeSources, setActiveSources] = useState(null);
  const [deletingDocumentId, setDeletingDocumentId] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("Connected"))
      .catch(() => setBackendStatus("Disconnected"));
  }, []);

  const handleUpload = async (files) => {
    setError("");

    const failedUploads = [];

    setUploading(true);

    try {
      for (const file of files) {
        if (
          file.type !== "application/pdf" &&
          !file.name.toLowerCase().endsWith(".pdf")
        ) {
          failedUploads.push(`${file.name}: Invalid PDF file.`);
          continue;
        }

        if (file.size > 20 * 1024 * 1024) {
          failedUploads.push(`${file.name}: File exceeds 20 MB.`);
          continue;
        }

        try {
          const result = await uploadPDF(file);

          setDocuments((previous) => {
            const alreadyExists = previous.some(
              (doc) => doc.document_id === result.document_id,
            );

            return alreadyExists ? previous : [...previous, result];
          });
        } catch (err) {
          failedUploads.push(`${file.name}: ${err.message}`);
        }
      }

      if (failedUploads.length > 0) {
        setError(failedUploads.join(" | "));
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (document) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.filename}"?\n\nThis will also delete its stored chunks from the knowledge base.`,
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setDeletingDocumentId(document.document_id);

    try {
      await deleteDocument(document.document_id);

      setDocuments((previous) =>
        previous.filter((doc) => doc.document_id !== document.document_id),
      );

      setActiveSources(null);
    } catch (err) {
      setError(`Failed to delete ${document.filename}: ${err.message}`);
    } finally {
      setDeletingDocumentId(null);
    }
  };

  const handleSend = async (question) => {
    setError("");
    setActiveSources(null);

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
    <div className="app-layout">
      <aside className="left-sidebar">
        <div className="brand">
          <div className="brand-icon">âœ¦</div>
          <div>
            <h1>Knowledge AI</h1>
            <span>Enterprise Assistant</span>
          </div>
        </div>

        <div className="sidebar-section">
          <p className="section-label">WORKSPACE</p>
          <div className="workspace-item">
            <span>â—ˆ</span>
            <span>Knowledge Base</span>
          </div>
        </div>

        <div className="sidebar-section document-section">
          <p className="section-label">YOUR DOCUMENTS</p>

          <FileUpload onUpload={handleUpload} uploading={uploading} />

          {documents.map((document) => (
            <div className="document-card" key={document.document_id}>
              <span className="pdf-icon">PDF</span>

              <div className="document-info">
                <strong>{document.filename}</strong>
                <small>{document.total_chunks} chunks processed</small>
              </div>

              <button
                type="button"
                className="delete-document-button"
                onClick={() => handleDelete(document)}
                disabled={deletingDocumentId !== null}
              >
                {deletingDocumentId === document.document_id
                  ? "Deleting..."
                  : "Delete"}
              </button>
            </div>
          ))}

          {documents.length === 0 && (
            <p className="section-label">No documents uploaded yet.</p>
          )}

          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="sidebar-footer">
          <span
            className={`status-dot ${
              backendStatus === "Connected"
                ? "online"
                : backendStatus === "Disconnected"
                  ? "offline"
                  : "checking"
            }`}
          />
          <span>Backend {backendStatus}</span>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-title">AI Assistant</span>
            <span className="topbar-subtitle">
              Ask questions about your documents
            </span>
          </div>

          <div className="connection-indicator">
            <span
              className={`status-dot ${
                backendStatus === "Connected" ? "online" : ""
              }`}
            />
            {backendStatus}
          </div>
        </header>

        <section className="chat-panel">
          <ChatWindow
            messages={messages}
            onSend={handleSend}
            loading={loading}
            onShowSources={setActiveSources}
          />
        </section>
      </main>

      {activeSources && (
        <aside className="sources-sidebar">
          <div className="sources-header">
            <div>
              <h2>Sources</h2>
              <p>{activeSources.length} references found</p>
            </div>

            <button
              className="close-sources"
              onClick={() => setActiveSources(null)}
              aria-label="Close sources"
            >
              Ã—
            </button>
          </div>

          <div className="sources-list">
            {activeSources.map((source, index) => (
              <div
                className="source-card"
                key={`${source.filename}-${source.page_number}-${index}`}
              >
                <div className="source-card-top">
                  <span className="pdf-icon">PDF</span>
                  <span className="source-number">Source {index + 1}</span>
                </div>

                <h3>{source.filename}</h3>

                <div className="source-meta">
                  <span>Page {source.page_number}</span>
                  <span>Score: {Number(source.score ?? 0).toFixed(3)}</span>
                </div>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}

export default App;
