// Mic capture and streamed playback for the AssemblyAI voice loop.
// Audio contract (backend <-> AssemblyAI, mirrored here): 24kHz mono
// 16-bit PCM. Browser -> backend frames are raw binary; backend -> browser
// audio arrives as base64 PCM inside a JSON {"type":"audio"} message.

const SAMPLE_RATE = 24000;
// 1024 samples @ 24kHz ~= 43ms, close to AssemblyAI's "~50ms works well" guidance.
const CAPTURE_BUFFER_SIZE = 1024;

function floatTo16BitPCM(input: Float32Array): ArrayBuffer {
  const buffer = new ArrayBuffer(input.length * 2);
  const view = new DataView(buffer);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]));
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

export class MicStreamer {
  private audioCtx: AudioContext;
  private stream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private onChunk: (chunk: ArrayBuffer) => void;

  constructor(onChunk: (chunk: ArrayBuffer) => void) {
    this.onChunk = onChunk;
    this.audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE });
  }

  async start(): Promise<void> {
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.source = this.audioCtx.createMediaStreamSource(this.stream);
    this.processor = this.audioCtx.createScriptProcessor(CAPTURE_BUFFER_SIZE, 1, 1);

    // ScriptProcessorNode only fires onaudioprocess while connected to a
    // destination; route through a muted gain node so the technician
    // doesn't hear their own mic looped back.
    const mute = this.audioCtx.createGain();
    mute.gain.value = 0;

    this.processor.onaudioprocess = (event) => {
      const input = event.inputBuffer.getChannelData(0);
      this.onChunk(floatTo16BitPCM(input));
    };

    this.source.connect(this.processor);
    this.processor.connect(mute);
    mute.connect(this.audioCtx.destination);
  }

  stop(): void {
    this.processor?.disconnect();
    this.source?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    this.processor = null;
    this.source = null;
    this.stream = null;
  }

  async close(): Promise<void> {
    this.stop();
    await this.audioCtx.close();
  }
}

export class AudioPlayer {
  private audioCtx: AudioContext;
  private nextStartTime = 0;

  constructor() {
    this.audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE });
  }

  playBase64Pcm(base64Data: string): void {
    const binary = atob(base64Data);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

    const view = new DataView(bytes.buffer);
    const sampleCount = bytes.length / 2;
    const float32 = new Float32Array(sampleCount);
    for (let i = 0; i < sampleCount; i++) {
      float32[i] = view.getInt16(i * 2, true) / 0x8000;
    }

    const buffer = this.audioCtx.createBuffer(1, float32.length, SAMPLE_RATE);
    buffer.copyToChannel(float32, 0);

    const source = this.audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(this.audioCtx.destination);

    const now = this.audioCtx.currentTime;
    const startAt = Math.max(now, this.nextStartTime);
    source.start(startAt);
    this.nextStartTime = startAt + buffer.duration;
  }

  reset(): void {
    this.nextStartTime = 0;
  }

  async close(): Promise<void> {
    await this.audioCtx.close();
  }
}
