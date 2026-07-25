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
    <main className="min-h-screen text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section className="overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/80 shadow-2xl shadow-cyan-950/25 backdrop-blur">
          <div className="grid gap-0 lg:grid-cols-[1.05fr_0.95fr]">
            <div className="relative border-b border-white/10 p-6 sm:p-8 lg:border-b-0 lg:border-r">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.12),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(249,115,22,0.10),transparent_24%)]" />
              <div className="relative space-y-6">
                <div className="inline-flex rounded-full border border-cyan-400/25 bg-cyan-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-cyan-200">
                  CartoonVerse
                </div>
                <div className="space-y-4">
                  <h1 className="max-w-xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                    Classical cartoonization for images, video, and emoji suggestions.
                  </h1>
                  <p className="max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
                    Upload a file, tune the smoothing and palette controls, and let the backend return a cartoonized
                    result. Image uploads also receive a rule-based WhatsApp-style emoji suggestion.
                  </p>
                </div>

                <div className="flex flex-wrap gap-3 text-sm">
                  <button
                    type="button"
                    onClick={() => setMode('image')}
                    className={`rounded-full px-4 py-2 transition ${
                      mode === 'image'
                        ? 'bg-cyan-400 text-slate-950'
                        : 'border border-white/15 bg-white/5 text-slate-200 hover:bg-white/10'
                    }`}
                  >
                    Image mode
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('video')}
                    className={`rounded-full px-4 py-2 transition ${
                      mode === 'video'
                        ? 'bg-cyan-400 text-slate-950'
                        : 'border border-white/15 bg-white/5 text-slate-200 hover:bg-white/10'
                    }`}
                  >
                    Video mode
                  </button>
                </div>

                <label
                  className="group flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-white/5 px-6 py-10 text-center transition hover:border-cyan-300/50 hover:bg-white/10"
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={(event) => {
                    event.preventDefault();
                    const droppedFile = event.dataTransfer.files.item(0);
                    void handleFileSelection(droppedFile);
                  }}
                >
                  <input
                    type="file"
                    accept="image/*,video/*"
                    className="hidden"
                    onChange={(event) => {
                      const selected = event.target.files?.item(0) || null;
                      void handleFileSelection(selected);
                    }}
                  />
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-white">Drop a file here or browse</p>
                    <p className="text-sm text-slate-400">Supported: {supportedExtensions}</p>
                  </div>
                  {file ? (
                    <div className="mt-5 rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3 text-left text-sm text-slate-300">
                      <div className="font-medium text-white">Selected file</div>
                      <div className="mt-1 break-all">{file.name}</div>
                      <div className="text-xs uppercase tracking-[0.25em] text-cyan-300">{mode}</div>
                    </div>
                  ) : null}
                </label>

                <div className="grid gap-4 sm:grid-cols-3">
                  <Slider
                    label="Edge threshold"
                    value={options.edgeThreshold}
                    min={0}
                    max={30}
                    onChange={(value) => setOptions((current) => ({ ...current, edgeThreshold: value }))}
                  />
                  <Slider
                    label="Palette size"
                    value={options.paletteSize}
                    min={2}
                    max={16}
                    onChange={(value) => setOptions((current) => ({ ...current, paletteSize: value }))}
                  />
                  <Slider
                    label="Smoothing"
                    value={options.smoothingStrength}
                    min={1}
                    max={10}
                    onChange={(value) => setOptions((current) => ({ ...current, smoothingStrength: value }))}
                  />
                </div>

                <button
                  type="button"
                  onClick={() => void handleProcess()}
                  disabled={loading || !file}
                  className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-300 to-amber-300 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? 'Processing...' : mode === 'image' ? 'Cartoonize image' : 'Queue video job'}
                </button>

                {error ? (
                  <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
                    {error}
                  </div>
                ) : null}
              </div>
            </div>

            <div className="space-y-6 p-6 sm:p-8">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-cyan-950/10">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Preview</p>
                    <h2 className="mt-1 text-xl font-semibold text-white">Before / after</h2>
                  </div>
                  <div className="rounded-full border border-white/10 bg-slate-900 px-3 py-1 text-xs text-slate-300">
                    {file ? formatStatus(videoJob?.status) : 'idle'}
                  </div>
                </div>

                <div className="mt-5 grid gap-4 lg:grid-cols-2">
                  <MediaCard title="Original" mediaUrl={previewUrl} mode={mode} emptyLabel="Select a file to preview it here." />
                  <MediaCard title="Cartoonized" mediaUrl={resultUrl} mode={mode} emptyLabel="Processed output will appear here." />
                </div>

                {mode === 'video' && videoJob ? (
                  <div className="mt-5 rounded-2xl border border-cyan-400/15 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-50">
                    <div className="font-medium">Video job {videoJob.job_id}</div>
                    <div className="mt-1 text-cyan-100/90">{jobProgressLabel}</div>
                  </div>
                ) : null}
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-xs uppercase tracking-[0.28em] text-fuchsia-300">Emoji suggestion</p>
                  <h2 className="mt-1 text-xl font-semibold text-white">Expression + skin tone</h2>
                  {emojiSuggestion ? (
                    <div className="mt-4 space-y-3 rounded-2xl border border-white/10 bg-slate-900/80 p-4">
                      <div className="text-4xl">🙂</div>
                      <div className="text-sm text-slate-300">{emojiSuggestion.emoji_name}</div>
                      <div className="text-sm text-slate-400">Expression: {emojiSuggestion.expression}</div>
                      <div className="text-sm text-slate-400">Skin tone: {emojiSuggestion.skin_tone}</div>
                      <div className="text-xs break-all text-slate-500">{emojiSuggestion.asset_path}</div>
                    </div>
                  ) : (
                    <p className="mt-4 text-sm leading-6 text-slate-400">
                      Image uploads will show the suggested emoji here. If no face is detected, the API returns a clear
                      response instead of failing silently.
                    </p>
                  )}
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-xs uppercase tracking-[0.28em] text-amber-300">Job status</p>
                  <h2 className="mt-1 text-xl font-semibold text-white">Video polling</h2>
                  <div className="mt-4 space-y-3 text-sm text-slate-300">
                    <div className="rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3">
                      <div className="font-medium text-white">Current status</div>
                      <div className="mt-1 capitalize text-slate-300">{videoJob?.status || 'idle'}</div>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3">
                      <div className="font-medium text-white">Next step</div>
                      <div className="mt-1 text-slate-300">
                        {videoJob?.status === 'done'
                          ? 'Download the processed video from the result pane.'
                          : 'Submit a video to queue a background job, then wait for the worker to finish.'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
    <label className="rounded-2xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-300">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.25em] text-slate-400">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="mt-4 h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-cyan-300"
      />
    </label>
  );
}

type MediaCardProps = {
  title: string;
  mediaUrl: string;
  mode: Mode;
  emptyLabel: string;
};

function MediaCard({ title, mediaUrl, mode, emptyLabel }: MediaCardProps) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
      <div className="border-b border-white/10 px-4 py-3 text-xs uppercase tracking-[0.25em] text-slate-400">
        {title}
      </div>
      <div className="flex min-h-72 items-center justify-center bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.05),transparent_50%)] p-4">
        {mediaUrl ? (
          mode === 'video' ? (
            <video src={mediaUrl} controls className="max-h-72 w-full rounded-xl object-contain" />
          ) : (
            <img src={mediaUrl} alt={title} className="max-h-72 w-full rounded-xl object-contain" />
          )
        ) : (
          <div className="max-w-xs text-center text-sm leading-6 text-slate-400">{emptyLabel}</div>
        )}
      </div>
    </div>
  );
}
