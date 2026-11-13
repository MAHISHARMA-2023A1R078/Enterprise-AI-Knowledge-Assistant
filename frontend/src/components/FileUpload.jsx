function FileUpload({ onUpload, uploading, uploadResult }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      onUpload(file);
      event.target.value = "";
    }
  };

  return (
    <div className="upload-section">
      <label htmlFor="pdf-upload" className="upload-button">
        {uploading ? "Uploading..." : "Upload PDF"}
      </label>

      <input
        id="pdf-upload"
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
        disabled={uploading}
        hidden
      />

      {uploadResult && (
        <div className="upload-success">
          <p>✓ {uploadResult.filename}</p>
          <small>{uploadResult.total_chunks} chunks processed</small>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
