import {Config} from '@remotion/cli/config';
import path from 'path';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);

// Set public directory to backend storage for accessing audio files
const storageDir = path.join(__dirname, '../backend/storage');
Config.setPublicDir(storageDir);
