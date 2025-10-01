<?php
/**
 * AnomRadar REST API - Main Entry Point
 */

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

use AnomRadar\Api\Database\Database;
use AnomRadar\Api\Controllers\ScanController;
use AnomRadar\Api\Controllers\ReportController;
use AnomRadar\Api\Controllers\WhitelistController;
use AnomRadar\Api\Utils\Response;
use AnomRadar\Api\Utils\Router;

// Load environment variables
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__ . '/..');
$dotenv->load();

// CORS headers
$allowedOrigins = explode(',', $_ENV['CORS_ALLOWED_ORIGINS'] ?? '*');
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowedOrigins) || in_array('*', $allowedOrigins)) {
    header('Access-Control-Allow-Origin: ' . ($origin ?: '*'));
}
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');
header('Content-Type: application/json; charset=utf-8');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Initialize database
try {
    $db = Database::getInstance();
} catch (Exception $e) {
    Response::error('Database connection failed', 500);
    exit;
}

// Initialize router
$router = new Router();

// Initialize controllers
$scanController = new ScanController($db);
$reportController = new ReportController($db);
$whitelistController = new WhitelistController($db);

// Define routes
// Scans
$router->get('/api/scans', [$scanController, 'list']);
$router->get('/api/scans/{id}', [$scanController, 'get']);
$router->post('/api/scans', [$scanController, 'create']);
$router->delete('/api/scans/{id}', [$scanController, 'delete']);

// Reports
$router->get('/api/reports/{scanId}', [$reportController, 'list']);
$router->post('/api/reports/{scanId}/html', [$reportController, 'generateHtml']);
$router->post('/api/reports/{scanId}/pdf', [$reportController, 'generatePdf']);
$router->get('/api/reports/{scanId}/download/{reportId}', [$reportController, 'download']);

// Whitelist
$router->get('/api/whitelist', [$whitelistController, 'list']);
$router->post('/api/whitelist', [$whitelistController, 'add']);
$router->delete('/api/whitelist/{id}', [$whitelistController, 'remove']);

// Health check
$router->get('/api/health', function() {
    Response::success(['status' => 'ok', 'timestamp' => time()]);
});

// Data purge endpoint (for cron job)
$router->post('/api/maintenance/purge', function() use ($db) {
    $retentionDays = (int)($_ENV['DATA_RETENTION_DAYS'] ?? 90);
    $cutoffDate = date('Y-m-d H:i:s', strtotime("-{$retentionDays} days"));
    
    $stmt = $db->prepare('DELETE FROM scans WHERE created_at < ?');
    $stmt->execute([$cutoffDate]);
    $deleted = $stmt->rowCount();
    
    Response::success(['deleted' => $deleted, 'cutoff_date' => $cutoffDate]);
});

// Dispatch request
try {
    $router->dispatch();
} catch (Exception $e) {
    Response::error($e->getMessage(), 500);
}
