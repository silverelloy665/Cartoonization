import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';

const client = axios.create({
  baseURL: apiBaseUrl,
});

export type ImageCartoonizeOptions = {
  edgeThreshold: number;
  paletteSize: number;
  smoothingStrength: number;
};

export type EmojiSuggestion = {
  expression: string;
  skin_tone: string;
  emoji_name: string;
  asset_path: string;
};

export type VideoJobSubmitResponse = {
  job_id: string;
  status: string;
  detail: string;
};

export type VideoJobStatusResponse = {
  job_id: string;
  status: 'queued' | 'processing' | 'done' | 'failed';
  output_path?: string | null;
  error?: string | null;
};

function buildFormData(file: File): FormData {
  const formData = new FormData();
  formData.append('file', file);
  return formData;
}

export async function cartoonizeImage(file: File, options: ImageCartoonizeOptions): Promise<Blob> {
  const response = await client.post('/cartoonize/image', buildFormData(file), {
    params: {
      edge_threshold: options.edgeThreshold,
      palette_size: options.paletteSize,
      smoothing_strength: options.smoothingStrength,
    },
    responseType: 'blob',
  });

  return response.data;
}

export async function suggestEmoji(file: File): Promise<EmojiSuggestion> {
  const response = await client.post('/suggest-emoji', buildFormData(file));
  return response.data as EmojiSuggestion;
}

export async function submitVideo(file: File, options: ImageCartoonizeOptions): Promise<VideoJobSubmitResponse> {
  const response = await client.post('/cartoonize/video', buildFormData(file), {
    params: {
      edge_threshold: options.edgeThreshold,
      palette_size: options.paletteSize,
      smoothing_strength: options.smoothingStrength,
    },
  });

  return response.data as VideoJobSubmitResponse;
}

export async function fetchVideoStatus(jobId: string): Promise<VideoJobStatusResponse> {
  const response = await client.get(`/cartoonize/video/status/${jobId}`);
  return response.data as VideoJobStatusResponse;
}

export async function fetchVideoResult(jobId: string): Promise<Blob> {
  const response = await client.get(`/cartoonize/video/result/${jobId}`, {
    responseType: 'blob',
  });

  return response.data;
}
