const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

async function build() {
  try {
    // Log environment variables for debugging
    console.log('Environment Variables:');
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('REACT_APP_API_BASE_URL:', process.env.REACT_APP_API_BASE_URL);
    
    // Ensure dist directory exists
    if (!fs.existsSync('dist')) {
      fs.mkdirSync('dist', { recursive: true });
    }
    if (!fs.existsSync('dist/js')) {
      fs.mkdirSync('dist/js', { recursive: true });
    }

    console.log('Building JavaScript with ESBuild...');
    
    const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'https://apush-grader-production.up.railway.app';
    console.log('Using API Base URL:', apiBaseUrl);

    // Build with esbuild
    await esbuild.build({
      entryPoints: ['src/index.tsx'],
      bundle: true,
      minify: true,
      outdir: 'dist/js',
      format: 'iife',
      target: ['es2020'],
      define: {
        'process.env.NODE_ENV': '"production"',
        'process.env.REACT_APP_API_BASE_URL': `"${apiBaseUrl}"`,
        'process.env': JSON.stringify({
          NODE_ENV: 'production',
          REACT_APP_API_BASE_URL: apiBaseUrl
        })
      },
      loader: {
        '.tsx': 'tsx',
        '.ts': 'tsx'
      },
      jsx: 'automatic',
      platform: 'browser'
    });

    console.log('JavaScript build completed!');

    // Copy index.html
    console.log('Copying index.html...');
    fs.copyFileSync('public/index.html', 'dist/index.html');
    console.log('Build completed successfully!');
    
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();