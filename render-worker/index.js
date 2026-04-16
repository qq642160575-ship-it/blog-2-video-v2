import { createClient } from 'redis';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const RENDER_QUEUE = 'render_queue';
const REMOTION_DIR = path.join(__dirname, '../remotion');
const STORAGE_DIR = path.join(__dirname, '../backend/storage');

class RenderWorker {
  constructor() {
    this.redis = null;
    this.isRunning = false;
  }

  async connect() {
    console.log('Connecting to Redis...');
    this.redis = createClient({ url: REDIS_URL });

    this.redis.on('error', (err) => {
      console.error('Redis error:', err);
    });

    await this.redis.connect();
    console.log('✓ Connected to Redis');
  }

  async disconnect() {
    if (this.redis) {
      await this.redis.quit();
      console.log('Disconnected from Redis');
    }
  }

  async popRenderTask(timeout = 0) {
    const result = await this.redis.brPop(RENDER_QUEUE, timeout);
    if (result) {
      return JSON.parse(result.element);
    }
    return null;
  }

  async renderVideo(task) {
    const { job_id, project_id, manifest_url } = task;

    console.log('============================================================');
    console.log(`Rendering Video`);
    console.log(`Job ID: ${job_id}`);
    console.log(`Project ID: ${project_id}`);
    console.log(`Manifest: ${manifest_url}`);
    console.log('============================================================');
    console.log();

    try {
      // Read manifest
      console.log('[1/3] Reading manifest...');
      const manifestPath = path.join(STORAGE_DIR, 'manifests', `${project_id}_manifest.json`);
      const manifestContent = await fs.readFile(manifestPath, 'utf-8');
      const manifest = JSON.parse(manifestContent);
      console.log(`  ✓ Loaded manifest with ${manifest.scenes.length} scenes`);
      console.log();

      // For now, render the first scene only (HookTitle)
      const firstScene = manifest.scenes[0];
      console.log('[2/3] Rendering scene...');
      console.log(`  Scene: ${firstScene.scene_id}`);
      console.log(`  Template: ${firstScene.template_type}`);

      // Calculate duration from start_ms and end_ms
      const durationMs = firstScene.end_ms - firstScene.start_ms;
      const durationSec = durationMs / 1000;
      console.log(`  Duration: ${durationSec}s`);
      console.log();

      // Prepare output path
      const outputDir = path.join(STORAGE_DIR, 'videos', project_id);
      await fs.mkdir(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, `${project_id}.mp4`);

      // Build props for Remotion
      // screen_text can be either array ["title", "subtitle"] or object {title, subtitle}
      const screenText = firstScene.template_props?.screen_text || firstScene.screen_text;
      let title, subtitle;

      if (Array.isArray(screenText)) {
        title = screenText[0] || 'Default Title';
        subtitle = screenText[1] || 'Default Subtitle';
      } else {
        title = screenText?.title || 'Default Title';
        subtitle = screenText?.subtitle || 'Default Subtitle';
      }

      // Load audio path if available
      let audioPath = null;
      if (firstScene.audio_path) {
        audioPath = path.join(STORAGE_DIR, firstScene.audio_path.replace(/^\.\/storage\//, ''));
        console.log(`  Audio: ${audioPath}`);
      }

      // Load subtitles if available
      let subtitles = null;
      const subtitlePath = path.join(STORAGE_DIR, 'subtitles', `${firstScene.scene_id}.srt`);
      try {
        const srtContent = await fs.readFile(subtitlePath, 'utf-8');
        subtitles = this.parseSRT(srtContent);
        console.log(`  Subtitles: ${subtitles.length} segments`);
      } catch (error) {
        console.log(`  Subtitles: Not found (optional)`);
      }

      const props = { title, subtitle, audioPath, subtitles };

      // Call Remotion CLI
      const durationInFrames = Math.round(durationSec * 30); // 30 fps
      await this.callRemotion('HookTitle', outputPath, props, durationInFrames);

      console.log();
      console.log('[3/3] Render complete!');
      console.log(`  ✓ Video saved: ${outputPath}`);
      console.log();

      // Update job status to completed
      await this.updateJobStatus(job_id, 'completed', 'export', 1.0, outputPath);

      console.log('============================================================');
      console.log(`✓ Job ${job_id} completed successfully!`);
      console.log('============================================================');
      console.log();

      return {
        success: true,
        video_url: `/storage/videos/${project_id}/${project_id}.mp4`,
      };
    } catch (error) {
      console.error();
      console.error('============================================================');
      console.error(`✗ Job ${job_id} failed!`);
      console.error(`Error: ${error.message}`);
      console.error('============================================================');
      console.error();
      throw error;
    }
  }

  async updateJobStatus(jobId, status, stage, progress, videoPath = null) {
    try {
      const payload = {
        status,
        stage,
        progress,
      };

      if (videoPath && status === 'completed') {
        // Extract relative path for video_url
        const videoUrl = videoPath.replace(/.*\/storage\//, '/storage/');
        payload.result_data = {
          video_url: videoUrl,
        };
      }

      await axios.patch(`${API_BASE_URL}/jobs/${jobId}/status`, payload);
      console.log(`  ✓ Job status updated: ${status} (${stage})`);
    } catch (error) {
      console.error(`  ⚠ Failed to update job status: ${error.message}`);
      // Don't throw - we still want to continue even if status update fails
    }
  }

  async callRemotion(compositionId, outputPath, props, durationInFrames) {
    return new Promise((resolve, reject) => {
      const propsJson = JSON.stringify(props);

      const args = [
        'render',
        'src/index.tsx',
        compositionId,
        outputPath,
        '--props', propsJson,
      ];

      if (durationInFrames) {
        args.push('--duration-in-frames', durationInFrames.toString());
      }

      console.log(`  Running: npx remotion ${args.join(' ')}`);
      console.log();

      const remotionProcess = spawn('npx', ['remotion', ...args], {
        cwd: REMOTION_DIR,
        stdio: 'inherit',
      });

      remotionProcess.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Remotion process exited with code ${code}`));
        }
      });

      remotionProcess.on('error', (err) => {
        reject(err);
      });
    });
  }

  parseSRT(srtContent) {
    const subtitles = [];
    const blocks = srtContent.trim().split('\n\n');

    for (const block of blocks) {
      const lines = block.split('\n');
      if (lines.length >= 3) {
        // Parse time range (e.g., "00:00:00,000 --> 00:00:01,489")
        const timeMatch = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
        if (timeMatch) {
          const startMs =
            parseInt(timeMatch[1]) * 3600000 + // hours
            parseInt(timeMatch[2]) * 60000 +    // minutes
            parseInt(timeMatch[3]) * 1000 +     // seconds
            parseInt(timeMatch[4]);             // milliseconds

          const endMs =
            parseInt(timeMatch[5]) * 3600000 +
            parseInt(timeMatch[6]) * 60000 +
            parseInt(timeMatch[7]) * 1000 +
            parseInt(timeMatch[8]);

          const text = lines.slice(2).join(' ');

          subtitles.push({
            text,
            start_ms: startMs,
            end_ms: endMs,
          });
        }
      }
    }

    return subtitles;
  }

  async run() {
    await this.connect();
    this.isRunning = true;

    console.log('============================================================');
    console.log('Render Worker Started');
    console.log('============================================================');
    console.log('Waiting for render tasks...');
    console.log();

    while (this.isRunning) {
      try {
        const task = await this.popRenderTask(5);

        if (task) {
          await this.renderVideo(task);
        }
      } catch (error) {
        console.error('Error processing task:', error);
        // Continue running even if one task fails
      }
    }

    await this.disconnect();
  }

  stop() {
    console.log('Stopping worker...');
    this.isRunning = false;
  }
}

// Main
const worker = new RenderWorker();

process.on('SIGINT', () => {
  console.log();
  worker.stop();
});

process.on('SIGTERM', () => {
  worker.stop();
});

worker.run().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
