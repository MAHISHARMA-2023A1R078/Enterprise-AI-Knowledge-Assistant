function FileUpload({ onUpload, uploading }) {
  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);

    if (files.length > 0) {
      onUpload(files);
    }

    event.target.value = "";
  };

  return (
    <div className="upload-section">
      <label htmlFor="pdf-upload" className="upload-button">
        {uploading ? "Uploading..." : "Upload PDFs"}
      </label>

      <input
        id="pdf-upload"
        type="file"
        accept=".pdf,application/pdf"
        multiple
        onChange={handleFileChange}
        disabled={uploading}
        hidden
      />
    </div>
  );
}

export default FileUpload;
