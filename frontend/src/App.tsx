import { useEffect, useMemo, useRef, useState } from 'react';

import {
  cartoonizeImage,
  fetchVideoResult,
  fetchVideoStatus,
  suggestEmoji,
  submitVideo,
  type EmojiSuggestion,
  type ImageCartoonizeOptions,
  type VideoJobStatusResponse,
} from './api';

type Mode = 'image' | 'video';

const defaultOptions: ImageCartoonizeOptions = {
  edgeThreshold: 9,
  paletteSize: 8,
  smoothingStrength: 5,
};

const supportedExtensions = 'PNG, JPG, JPEG, WEBP, MP4, MOV, WEBM';

function getFileMode(file: File): Mode {
  return file.type.startsWith('video/') ? 'video' : 'image';
}

function formatStatus(status?: VideoJobStatusResponse['status']): string {
  if (!status) {
    return 'idle';
  }
  return status;
}

export default function App() {
  const [mode, setMode] = useState<Mode>('image');
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [resultUrl, setResultUrl] = useState<string>('');
  const [emojiSuggestion, setEmojiSuggestion] = useState<EmojiSuggestion | null>(null);
  const [videoJob, setVideoJob] = useState<VideoJobStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [options, setOptions] = useState<ImageCartoonizeOptions>(defaultOptions);
  const [dragActive, setDragActive] = useState(false);
  const pollingRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      if (resultUrl) {
        URL.revokeObjectURL(resultUrl);
      }
      if (pollingRef.current) {
        window.clearInterval(pollingRef.current);
      }
    };
  }, [previewUrl, resultUrl]);

  const jobProgressLabel = useMemo(() => {
    if (!videoJob) {
      return 'No job queued yet.';
    }
    if (videoJob.status === 'queued') {
      return 'Queued and waiting for the worker.';
    }
    if (videoJob.status === 'processing') {
      return 'Worker is processing the video frame by frame.';
    }
    if (videoJob.status === 'done') {
      return 'Processing complete.';
    }
    return videoJob.error || 'Processing failed.';
  }, [videoJob]);

  const isActive = Boolean(file) && !loading;

  async function handleFileSelection(nextFile: File | null) {
    setError('');
    setEmojiSuggestion(null);
    setVideoJob(null);
    setResultUrl('');
    setFile(nextFile);

    if (!nextFile) {
      setPreviewUrl('');
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    const nextPreviewUrl = URL.createObjectURL(nextFile);
    setPreviewUrl(nextPreviewUrl);
    setMode(getFileMode(nextFile));
  }

  async function handleProcess() {
    if (!file) {
      setError('Pick an image or video first.');
      return;
    }

    setLoading(true);
    setError('');
    setEmojiSuggestion(null);
    setResultUrl('');

    try {
      if (mode === 'image') {
        const [cartoonBlob, emoji] = await Promise.all([
          cartoonizeImage(file, options),
          suggestEmoji(file).catch((emojiError: unknown) => {
            if (emojiError && typeof emojiError === 'object' && 'response' in emojiError) {
              const response = (emojiError as { response?: { data?: { detail?: string } } }).response;
              if (response?.data?.detail) {
                setError(response.data.detail);
              }
            }
            return null;
          }),
        ]);

        const imageUrl = URL.createObjectURL(cartoonBlob);
        setResultUrl(imageUrl);
        if (emoji) {
          setEmojiSuggestion(emoji);
        }
      } else {
        const job = await submitVideo(file, options);
        setVideoJob(job);

        if (pollingRef.current) {
          window.clearInterval(pollingRef.current);
        }

        pollingRef.current = window.setInterval(async () => {
          try {
            const status = await fetchVideoStatus(job.job_id);
            setVideoJob(status);

            if (status.status === 'done') {
              if (pollingRef.current) {
                window.clearInterval(pollingRef.current);
                pollingRef.current = null;
              }
              const resultBlob = await fetchVideoResult(job.job_id);
              const nextResultUrl = URL.createObjectURL(resultBlob);
              setResultUrl(nextResultUrl);
              setLoading(false);
            }

            if (status.status === 'failed') {
              if (pollingRef.current) {
                window.clearInterval(pollingRef.current);
                pollingRef.current = null;
              }
              setError(status.error || 'Video processing failed.');
              setLoading(false);
            }
          } catch (pollError) {
            if (pollingRef.current) {
              window.clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            setError(pollError instanceof Error ? pollError.message : 'Unable to poll video job.');
            setLoading(false);
          }
        }, 2000);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Processing failed.');
      setLoading(false);
    } finally {
      if (mode === 'image') {
        setLoading(false);
      }
    }
  }

  return (
    <main className="app-shell">
      <div className="page-shell">
        <header className="hero-copy">
          <p className="eyebrow">CartoonVerse</p>
          <h1>See your photo in bold ink lines and flat color fills.</h1>
          <p className="hero-subtitle">
            Drop an image or video, tune the cartoon pipeline, and watch your result appear in the same comic-style
            frame the app would produce.
          </p>
        </header>

        <section className="hero-panels">
          <article className="panel panel--hero">
            <div className="panel-header">
              <span>Before</span>
            </div>
            <div className="panel-content">
              <MediaPreview url={previewUrl} mode={mode} label="Original media preview" />
            </div>
          </article>
          <article className="panel panel--hero panel--accent">
            <div className="panel-header">
              <span>After</span>
            </div>
            <div className="panel-content">
              <MediaPreview url={resultUrl} mode={mode} label="Cartoonized result preview" />
            </div>
          </article>
        </section>

        <section className="panel-grid">
          <article className={`panel upload-panel ${dragActive ? 'upload-active' : ''}`}>
            <div className="panel-header">
              <span>Drop zone</span>
            </div>
            <div
              className="upload-body"
              onDragEnter={(event) => {
                event.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={(event) => {
                event.preventDefault();
                setDragActive(false);
              }}
              onDragOver={(event) => {
                event.preventDefault();
              }}
              onDrop={(event) => {
                event.preventDefault();
                setDragActive(false);
                const droppedFile = event.dataTransfer.files.item(0);
                void handleFileSelection(droppedFile);
              }}
            >
              <input
                type="file"
                accept="image/*,video/*"
                className="upload-input"
                onChange={(event) => {
                  const selected = event.target.files?.item(0) || null;
                  void handleFileSelection(selected);
                }}
              />
              <div className="upload-icon" aria-hidden="true">
                <svg viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M24 10v20" strokeLinecap="round" />
                  <path d="M16 18l8-8 8 8" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M12 32v4a4 4 0 0 0 4 4h16a4 4 0 0 0 4-4v-4" strokeLinecap="round" />
                </svg>
              </div>
              <div className="upload-copy">
                <p className="upload-title">Drop your photo here to see it cartoonized</p>
                <p className="upload-subtitle">Supported: {supportedExtensions}</p>
              </div>
              {file ? (
                <div className="upload-selected" aria-live="polite">
                  <strong>{file.name}</strong>
                  <span>{mode} file ready</span>
                </div>
              ) : null}
            </div>
          </article>

          <article className="panel panel--controls">
            <div className="panel-header">
              <span>Controls</span>
            </div>
            <div className="mode-toggle" role="group" aria-label="Choose cartoon mode">
              <button
                type="button"
                onClick={() => setMode('image')}
                className={mode === 'image' ? 'button button--solid' : 'button button--ghost'}
              >
                Image
              </button>
              <button
                type="button"
                onClick={() => setMode('video')}
                className={mode === 'video' ? 'button button--solid' : 'button button--ghost'}
              >
                Video
              </button>
            </div>

            <div className="sliders-grid">
              <Slider label="Edge threshold" value={options.edgeThreshold} min={0} max={30} onChange={(value) => setOptions((current) => ({ ...current, edgeThreshold: value }))} />
              <Slider label="Palette size" value={options.paletteSize} min={2} max={16} onChange={(value) => setOptions((current) => ({ ...current, paletteSize: value }))} />
              <Slider label="Smoothing" value={options.smoothingStrength} min={1} max={10} onChange={(value) => setOptions((current) => ({ ...current, smoothingStrength: value }))} />
            </div>

            <button type="button" disabled={!file || loading} onClick={() => void handleProcess()} className="button button--action">
              {loading ? 'Processing…' : mode === 'image' ? 'Cartoonize this' : 'Queue video job'}
            </button>

            {error ? <div className="banner banner--error">{error}</div> : null}
          </article>
        </section>

        <section className="result-grid">
          <article className="panel panel--pipeline">
            <div className="panel-header">
              <span>Processing</span>
            </div>
            <div className="panel-body">
              <ProcessingPipeline active={loading || Boolean(videoJob?.status === 'processing' || videoJob?.status === 'queued')} />
              <div className="status-copy">
                {videoJob ? <span>Job #{videoJob.job_id}</span> : <span>Submit a file to start the cartoon pipeline.</span>}
                <p>{jobProgressLabel}</p>
              </div>
            </div>
          </article>

          <article className="panel panel--emoji">
            <div className="speech-bubble">
              <div className="speech-header">Emoji suggestion</div>
              {emojiSuggestion ? (
                <div className="speech-body">
                  <div className="emoji-display" aria-label={`Suggested emoji ${emojiSuggestion.emoji_name}`}>
                    <img
                      src={`https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/${emojiSuggestion.emoji_codepoint}.png`}
                      alt={emojiSuggestion.emoji_name}
                      width={48}
                      height={48}
                      onError={(event) => {
                        const target = event.currentTarget as HTMLImageElement;
                        target.onerror = null;
                        target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-size='36'%3E${String.fromCodePoint(parseInt(emojiSuggestion.emoji_codepoint, 16))}%3C/text%3E%3C/svg%3E`;
                      }}
                    />
                  </div>
                  <p>
                    You looked {emojiSuggestion.expression.toLowerCase()} — here&apos;s your match.
                  </p>
                  <dl>
                    <div>
                      <dt>Expression</dt>
                      <dd>{emojiSuggestion.expression}</dd>
                    </div>
                    <div>
                      <dt>Skin tone</dt>
                      <dd>{emojiSuggestion.skin_tone}</dd>
                    </div>
                  </dl>
                </div>
              ) : (
                <div className="speech-body">
                  <p>No emoji yet. Upload an image so CartoonVerse can suggest a match.</p>
                </div>
              )}
            </div>
          </article>
        </section>

        <section className="panel panel--comparison">
          <div className="panel-header">
            <span>Result view</span>
          </div>
          <div className="panel-content">
            <ResultComparison beforeUrl={previewUrl} afterUrl={resultUrl} mode={mode} />
            {resultUrl ? (
              <a className="button button--secondary" href={resultUrl} download={file?.name ? `cartoon-${file.name}` : 'cartoon-result'}>
                Download result
              </a>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  );
}

type SliderProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
};

function Slider({ label, value, min, max, onChange }: SliderProps) {
  return (
    <label className="control-card">
      <div className="control-header">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="range-input"
      />
    </label>
  );
}

type MediaPreviewProps = {
  url: string;
  mode: Mode;
  label: string;
};

function MediaPreview({ url, mode, label }: MediaPreviewProps) {
  if (!url) {
    return <div className="empty-state">No media selected yet.</div>;
  }

  return mode === 'video' ? (
    <video className="media-display" src={url} controls aria-label={label} />
  ) : (
    <img className="media-display" src={url} alt={label} />
  );
}

type ResultComparisonProps = {
  beforeUrl: string;
  afterUrl: string;
  mode: Mode;
};

function ResultComparison({ beforeUrl, afterUrl, mode }: ResultComparisonProps) {
  const [sliderValue, setSliderValue] = useState(50);

  if (!beforeUrl || !afterUrl) {
    return <div className="comparison-empty">Drop a file and process it to enable the draggable comparison slider.</div>;
  }

  return (
    <div className="comparison-shell">
      <div className="comparison-frame">
        <div className="comparison-layer comparison-before">
          {mode === 'video' ? (
            <video className="comparison-media" src={beforeUrl} muted playsInline />
          ) : (
            <img className="comparison-media" src={beforeUrl} alt="Original before cartoonization" />
          )}
        </div>
        <div className="comparison-layer comparison-after" style={{ width: `${sliderValue}%` }}>
          {mode === 'video' ? (
            <video className="comparison-media" src={afterUrl} muted playsInline />
          ) : (
            <img className="comparison-media" src={afterUrl} alt="Cartoonized after image" />
          )}
        </div>
        <div className="comparison-divider" style={{ left: `${sliderValue}%` }} aria-hidden="true" />
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={sliderValue}
        onChange={(event) => setSliderValue(Number(event.target.value))}
        className="comparison-slider"
        aria-label="Compare before and after"
      />
    </div>
  );
}

function ProcessingPipeline({ active }: { active: boolean }) {
  return (
    <div className="pipeline-shell" role="status" aria-live="polite">
      <div className={`pipeline-step ${active ? 'pipeline-step--active' : ''}`}> 
        <div className="pipeline-icon">✏️</div>
        <p>Edge sketch</p>
      </div>
      <div className={`pipeline-step ${active ? 'pipeline-step--active delay-1' : ''}`}>
        <div className="pipeline-icon">🎨</div>
        <p>Flat color</p>
      </div>
      <div className={`pipeline-step ${active ? 'pipeline-step--active delay-2' : ''}`}>
        <div className="pipeline-icon">✅</div>
        <p>Final render</p>
      </div>
    </div>
  );
}
