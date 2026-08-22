import type { ChangeEvent } from "react"

type Props = {
  selectedFile: File | null
  previewUrl: string | null
  disabled: boolean
  onFileChange: (file: File | null) => void
}

function ImageUpload({ selectedFile, previewUrl, disabled, onFileChange }: Props) {
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onFileChange(event.target.files?.[0] ?? null)
  }

  return (
    <div className="image-upload">
      <div className={`image-stage${previewUrl ? " has-image" : ""}`}>
        {previewUrl ? <img src={previewUrl} alt="분석할 얼굴 사진 미리보기" /> : (
          <div className="upload-placeholder" aria-hidden="true">
            <span className="upload-icon">＋</span>
            <strong>분석할 사진을 선택하세요</strong>
            <span>JPG, PNG 등 이미지 파일</span>
          </div>
        )}
        <div className="image-overlay-layer" aria-hidden="true" />
      </div>
      <div className="file-controls">
        <label className={`file-button${disabled ? " is-disabled" : ""}`}>
          <span>{selectedFile ? "다른 사진 선택" : "사진 선택"}</span>
          <input type="file" accept="image/*" disabled={disabled} onChange={handleChange} />
        </label>
        <p className="file-name">
          {selectedFile ? selectedFile.name : "선택된 파일이 없습니다."}
        </p>
      </div>
    </div>
  )
}

export default ImageUpload
