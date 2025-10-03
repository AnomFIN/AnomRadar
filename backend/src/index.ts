import dotenv from 'dotenv';
import { logger } from './utils/logger';
import { Config } from './config/config';
import { ScannerOrchestrator } from './scanners/orchestrator';

// Load environment variables
dotenv.config();

/**
 * AnomRadar Backend Scanner
 * Main entry point for the OSINT scanning service
 */
class AnomRadarBackend {
  private orchestrator: ScannerOrchestrator;
  private config: Config;

  constructor() {
    this.config = new Config();
    this.orchestrator = new ScannerOrchestrator(this.config);
  }

  async start(): Promise<void> {
    logger.info('Starting AnomRadar Backend Scanner...');
    
    if (this.config.simulationMode) {
      logger.warn('⚠️  SIMULATION MODE IS ENABLED - No real scans will be performed');
      logger.warn('⚠️  Set SIMULATION_MODE=false in .env to enable real scanning');
    }

    // Initialize orchestrator
    await this.orchestrator.initialize();
    
    logger.info('✓ AnomRadar Backend Scanner is ready');
    logger.info(`  Simulation Mode: ${this.config.simulationMode ? 'ON' : 'OFF'}`);
    logger.info(`  Max Concurrent Scans: ${this.config.maxConcurrentScans}`);
    logger.info(`  Notifications: ${this.config.notificationsEnabled ? 'ENABLED (whitelist only)' : 'DISABLED'}`);
  }

  async shutdown(): Promise<void> {
    logger.info('Shutting down AnomRadar Backend Scanner...');
    await this.orchestrator.shutdown();
    logger.info('✓ Shutdown complete');
  }
}

// Main execution
const backend = new AnomRadarBackend();

// Graceful shutdown handlers
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received');
  await backend.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received');
  await backend.shutdown();
  process.exit(0);
});

// Start the backend
backend.start().catch((error) => {
  logger.error('Failed to start AnomRadar Backend:', error);
  process.exit(1);
});
