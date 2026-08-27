import type { ChangeEvent, DragEvent } from "react"
import {useRef, useState,} from "react"

type Props = {
  selectedFile: File | null
  previewUrl: string | null
  disabled: boolean
  hairlineYRatio: number | null
  onHairlineChange: (ratio: number) => void
  onFileChange: (file: File | null) => void
}

function ImageUpload({ selectedFile, previewUrl, disabled, hairlineYRatio, onHairlineChange, onFileChange }: Props) {
  const imageWrapperRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [isDragging, setIsDragging] = useState(false)
  const [isFileDragging, setIsFileDragging] = useState(false)
  

  console.log(isDragging)
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    onFileChange(event.target.files?.[0] ?? null) // 선택된 파일이 없으면 null로 전달
  }

  function handlePointerMove(event: React.PointerEvent<HTMLDivElement>) {
    if (!isDragging || !imageWrapperRef.current) return

    const rect = imageWrapperRef.current.getBoundingClientRect()

    const y = event.clientY - rect.top
    const ratio = y / rect.height

    const clampedRatio = Math.max(0, Math.min(0.995, ratio)) // 0과 1 사이로 제한

    onHairlineChange(clampedRatio)
  }

  function handlePointerDown(event: React.PointerEvent<HTMLDivElement>) {
    setIsDragging(true)
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  function handlePointerUp(event: React.PointerEvent<HTMLDivElement>) {
    setIsDragging(false)
    event.currentTarget.releasePointerCapture(event.pointerId)
  }

  function handleStageClick() {
    if (disabled) return

    fileInputRef.current?.click()
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()

    if (disabled) return

    setIsFileDragging(true)
  }
  function handleDragLeave() {
    setIsFileDragging(false)
  }
  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setIsFileDragging(false)

    if (disabled) return

    const file = event.dataTransfer.files?.[0]

    if (!file) return

    if (!file.type.startsWith("image/")) return

    onFileChange(file)
  }

  return (
    <div className="image-upload">
      <div
        className={`image-stage${previewUrl ? " has-image" : ""}${isFileDragging ? " is-dragging" : ""}`}
        onClick={handleStageClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {previewUrl ? (
          <div className="image-preview-wrapper"
          ref={imageWrapperRef}
          >
            <img
              src={previewUrl}
              alt="분석할 얼굴 사진 미리보기"
            />

            {hairlineYRatio !== null && (
              <div
                className="hairline-guide"
                style={{
                  top: `${hairlineYRatio * 100}%`,
                }}
                onPointerDown={(event) => {
                  event.stopPropagation()
                  handlePointerDown(event)
                }}
                onPointerMove={handlePointerMove}
                onPointerUp={handlePointerUp}
              >
                <div className="hairline-handle" />
              </div>
            )}
          </div>
        ) : (
          <div className="upload-placeholder" aria-hidden="true">
            <span className="upload-icon">＋</span>
            <strong>분석할 사진을 선택하세요</strong>
            <span>클릭하거나 이미지를 드래그하세요</span>
            <small>JPG, PNG 등 이미지파일</small>
          </div>
        )}

        <div className="image-overlay-layer" aria-hidden="true" />
      </div>

      <div className="file-controls">
        <label className={`file-button${disabled ? " is-disabled" : ""}`}>
          <span>{selectedFile ? "다른 사진 선택" : "사진 선택"}</span>
          <input type="file" accept="image/*" disabled={disabled} onChange={handleChange} ref={fileInputRef} />
        </label>
        <p className="file-name">
          {selectedFile ? selectedFile.name : "선택된 파일이 없습니다."}
        </p>
      </div>
    </div>
  )
}

export default ImageUpload
