// Node.js Performance Profiling Configuration Template
//
// Use with clinic.js for comprehensive profiling
// Install: npm install -g clinic

module.exports = {
  // ============================================================
  // Clinic.js Configuration
  // ============================================================

  clinic: {
    // CPU profiling (flame graph)
    flame: {
      command: 'node app.js',
      sampleInterval: 10, // ms
      detectPort: true,
      debug: false
    },

    // Event loop delay profiling
    doctor: {
      command: 'node app.js',
      sampleInterval: 10,
      detectPort: true,
      debug: false
    },

    // Async operations profiling
    bubbleprof: {
      command: 'node app.js',
      detectPort: true,
      debug: false
    }
  },

  // ============================================================
  // V8 Profiler Configuration
  // ============================================================

  v8: {
    // CPU profiling
    cpuProfile: {
      enabled: process.env.NODE_ENV !== 'production',
      interval: 1000, // Sampling interval in microseconds
      outputPath: './profiles/cpu-profile-${Date.now()}.cpuprofile'
    },

    // Heap snapshot
    heapSnapshot: {
      enabled: true,
      interval: 60 * 60 * 1000, // Every hour
      outputPath: './profiles/heap-${Date.now()}.heapsnapshot',
      maxSnapshots: 5 // Keep last 5 snapshots
    },

    // Heap statistics
    heapStats: {
      enabled: true,
      interval: 10000, // Every 10 seconds
      thresholds: {
        heapUsedMB: 800,      // Alert if heap usage > 800MB
        externalMB: 100,       // Alert if external memory > 100MB
        arrayBuffersMB: 50     // Alert if array buffers > 50MB
      }
    }
  },

  // ============================================================
  // Performance Monitoring
  // ============================================================

  monitoring: {
    // Event loop lag monitoring
    eventLoop: {
      enabled: true,
      warningThreshold: 50, // ms
      criticalThreshold: 100 // ms
    },

    // GC monitoring
    gc: {
      enabled: true,
      logSlowGC: true,
      slowGCThreshold: 100 // ms
    },

    // Memory leak detection
    memoryLeak: {
      enabled: true,
      checkInterval: 60000, // 1 minute
      growthThreshold: 10, // Alert if heap grows for 10 consecutive checks
      action: 'snapshot' // 'snapshot' | 'alert' | 'restart'
    }
  },

  // ============================================================
  // APM Integration (Example: Datadog)
  // ============================================================

  apm: {
    enabled: process.env.NODE_ENV === 'production',
    provider: 'datadog', // 'datadog' | 'newrelic' | 'elastic'
    config: {
      service: process.env.SERVICE_NAME || 'my-service',
      env: process.env.NODE_ENV || 'development',
      version: process.env.SERVICE_VERSION || '1.0.0',

      // Profiling
      profiling: true,
      runtimeMetrics: true,

      // Sampling
      sampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0
    }
  }
};

// ============================================================
// Profiling Setup Functions
// ============================================================

function setupCPUProfiling() {
  const v8 = require('v8');
  const fs = require('fs');
  const path = require('path');

  const config = module.exports.v8.cpuProfile;
  if (!config.enabled) return;

  // Create profiles directory
  const profilesDir = path.dirname(config.outputPath);
  if (!fs.existsSync(profilesDir)) {
    fs.mkdirSync(profilesDir, { recursive: true });
  }

  // Start profiling on SIGUSR1
  process.on('SIGUSR1', () => {
    const startTime = Date.now();
    const outputPath = config.outputPath.replace('${Date.now()}', startTime);

    console.log(`Starting CPU profile: ${outputPath}`);

    // Note: Requires --prof flag or inspector API
    // This is a simplified example
    console.log('Use: node --prof app.js');
    console.log('Then: node --prof-process isolate-*.log > profile.txt');
  });
}

function setupHeapSnapshots() {
  const v8 = require('v8');
  const fs = require('fs');
  const path = require('path');

  const config = module.exports.v8.heapSnapshot;
  if (!config.enabled) return;

  // Create profiles directory
  const profilesDir = path.dirname(config.outputPath);
  if (!fs.existsSync(profilesDir)) {
    fs.mkdirSync(profilesDir, { recursive: true });
  }

  function takeSnapshot() {
    const outputPath = config.outputPath.replace('${Date.now()}', Date.now());
    console.log(`Taking heap snapshot: ${outputPath}`);
    v8.writeHeapSnapshot(outputPath);

    // Cleanup old snapshots
    cleanupOldSnapshots(profilesDir, config.maxSnapshots);
  }

  // Take snapshot on SIGUSR2
  process.on('SIGUSR2', takeSnapshot);

  // Periodic snapshots
  if (config.interval) {
    setInterval(takeSnapshot, config.interval);
  }
}

function cleanupOldSnapshots(dir, maxSnapshots) {
  const fs = require('fs');
  const path = require('path');

  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.heapsnapshot'))
    .map(f => ({
      name: f,
      path: path.join(dir, f),
      time: fs.statSync(path.join(dir, f)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time);

  // Delete old files
  files.slice(maxSnapshots).forEach(file => {
    fs.unlinkSync(file.path);
    console.log(`Deleted old snapshot: ${file.name}`);
  });
}

function setupHeapMonitoring() {
  const config = module.exports.v8.heapStats;
  if (!config.enabled) return;

  setInterval(() => {
    const usage = process.memoryUsage();
    const heapUsedMB = Math.round(usage.heapUsed / 1024 / 1024);
    const externalMB = Math.round(usage.external / 1024 / 1024);
    const arrayBuffersMB = Math.round(usage.arrayBuffers / 1024 / 1024);

    console.log({
      heapUsedMB,
      heapTotalMB: Math.round(usage.heapTotal / 1024 / 1024),
      externalMB,
      arrayBuffersMB,
      rssMB: Math.round(usage.rss / 1024 / 1024)
    });

    // Alert on threshold breach
    if (heapUsedMB > config.thresholds.heapUsedMB) {
      console.error(`Heap usage above threshold: ${heapUsedMB}MB > ${config.thresholds.heapUsedMB}MB`);
    }
    if (externalMB > config.thresholds.externalMB) {
      console.error(`External memory above threshold: ${externalMB}MB > ${config.thresholds.externalMB}MB`);
    }
    if (arrayBuffersMB > config.thresholds.arrayBuffersMB) {
      console.error(`Array buffers above threshold: ${arrayBuffersMB}MB > ${config.thresholds.arrayBuffersMB}MB`);
    }
  }, config.interval);
}

function setupEventLoopMonitoring() {
  const config = module.exports.monitoring.eventLoop;
  if (!config.enabled) return;

  let lastCheck = Date.now();

  setInterval(() => {
    const now = Date.now();
    const lag = now - lastCheck - 100; // 100ms is the interval

    if (lag > config.criticalThreshold) {
      console.error(`Event loop lag CRITICAL: ${lag}ms`);
    } else if (lag > config.warningThreshold) {
      console.warn(`Event loop lag WARNING: ${lag}ms`);
    }

    lastCheck = now;
  }, 100);
}

function setupMemoryLeakDetection() {
  const config = module.exports.monitoring.memoryLeak;
  if (!config.enabled) return;

  let lastHeapUsed = 0;
  let growthCount = 0;

  setInterval(() => {
    const currentHeapUsed = process.memoryUsage().heapUsed;

    if (currentHeapUsed > lastHeapUsed) {
      growthCount++;
      if (growthCount >= config.growthThreshold) {
        console.error(`Possible memory leak detected (heap growing for ${growthCount} checks)`);

        if (config.action === 'snapshot') {
          const v8 = require('v8');
          const filename = `./profiles/leak-${Date.now()}.heapsnapshot`;
          v8.writeHeapSnapshot(filename);
          console.log(`Heap snapshot taken: ${filename}`);
        }

        growthCount = 0;
      }
    } else {
      growthCount = 0;
    }

    lastHeapUsed = currentHeapUsed;
  }, config.checkInterval);
}

// ============================================================
// Initialize Profiling
// ============================================================

function initializeProfiling() {
  console.log('Initializing performance profiling...');

  setupCPUProfiling();
  setupHeapSnapshots();
  setupHeapMonitoring();
  setupEventLoopMonitoring();
  setupMemoryLeakDetection();

  console.log('Profiling enabled. Send SIGUSR1 for CPU profile, SIGUSR2 for heap snapshot.');
}

// Auto-initialize if required directly
if (require.main === module) {
  initializeProfiling();
}

module.exports.initializeProfiling = initializeProfiling;

// ============================================================
// Usage Examples
// ============================================================

/*
1. Enable profiling in application:

   const profiling = require('./profiling-config');
   profiling.initializeProfiling();

2. Take heap snapshot:

   kill -SIGUSR2 $(pgrep -f "node app.js")

3. Run with clinic.js:

   clinic doctor -- node app.js
   clinic flame -- node app.js
   clinic bubbleprof -- node app.js

4. Built-in profiler:

   node --prof app.js
   node --prof-process isolate-*.log > profile.txt

5. Chrome DevTools:

   node --inspect app.js
   # Open chrome://inspect
*/
