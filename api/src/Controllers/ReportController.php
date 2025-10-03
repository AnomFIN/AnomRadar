<?php

declare(strict_types=1);

namespace AnomRadar\Api\Controllers;

use AnomRadar\Api\Database\Database;
use AnomRadar\Api\Utils\Response;
use AnomRadar\Api\Reports\HtmlReportGenerator;
use AnomRadar\Api\Reports\PdfReportGenerator;

/**
 * Report Controller - Manages report generation
 */
class ReportController
{
    private Database $db;
    private string $outputPath;

    public function __construct(Database $db)
    {
        $this->db = $db;
        $this->outputPath = $_ENV['REPORT_OUTPUT_PATH'] ?? '/tmp/reports';
        
        if (!is_dir($this->outputPath)) {
            mkdir($this->outputPath, 0755, true);
        }
    }

    public function list(string $scanId): void
    {
        // Get scan
        $stmt = $this->db->prepare('SELECT id FROM scans WHERE scan_id = ?');
        $stmt->execute([$scanId]);
        $scan = $stmt->fetch();

        if (!$scan) {
            Response::notFound('Scan not found');
        }

        // Get reports
        $stmt = $this->db->prepare('SELECT * FROM reports WHERE scan_id = ? ORDER BY generated_at DESC');
        $stmt->execute([$scan['id']]);
        $reports = $stmt->fetchAll();

        Response::success(['reports' => $reports]);
    }

    public function generateHtml(string $scanId): void
    {
        $scan = $this->getScanData($scanId);
        
        $generator = new HtmlReportGenerator();
        $html = $generator->generate($scan);
        
        $filename = "report_{$scanId}_" . time() . ".html";
        $filepath = $this->outputPath . '/' . $filename;
        file_put_contents($filepath, $html);

        // Save to database
        $stmt = $this->db->prepare(
            'INSERT INTO reports (scan_id, report_type, file_path, file_size) VALUES (?, ?, ?, ?)'
        );
        $stmt->execute([$scan['id'], 'html', $filepath, filesize($filepath)]);
        $reportId = $this->db->lastInsertId();

        Response::success([
            'report_id' => $reportId,
            'filename' => $filename,
            'download_url' => "/api/reports/{$scanId}/download/{$reportId}",
        ]);
    }

    public function generatePdf(string $scanId): void
    {
        $scan = $this->getScanData($scanId);
        
        $generator = new PdfReportGenerator();
        $filepath = $generator->generate($scan, $this->outputPath);

        // Save to database
        $stmt = $this->db->prepare(
            'INSERT INTO reports (scan_id, report_type, file_path, file_size) VALUES (?, ?, ?, ?)'
        );
        $stmt->execute([$scan['id'], 'pdf', $filepath, filesize($filepath)]);
        $reportId = $this->db->lastInsertId();

        Response::success([
            'report_id' => $reportId,
            'filename' => basename($filepath),
            'download_url' => "/api/reports/{$scanId}/download/{$reportId}",
        ]);
    }

    public function download(string $scanId, string $reportId): void
    {
        $stmt = $this->db->prepare('SELECT r.*, s.scan_id FROM reports r JOIN scans s ON r.scan_id = s.id WHERE r.id = ? AND s.scan_id = ?');
        $stmt->execute([$reportId, $scanId]);
        $report = $stmt->fetch();

        if (!$report || !file_exists($report['file_path'])) {
            Response::notFound('Report not found');
        }

        $contentType = $report['report_type'] === 'pdf' ? 'application/pdf' : 'text/html';
        header('Content-Type: ' . $contentType);
        header('Content-Disposition: attachment; filename="' . basename($report['file_path']) . '"');
        header('Content-Length: ' . $report['file_size']);
        readfile($report['file_path']);
        exit;
    }

    private function getScanData(string $scanId): array
    {
        $stmt = $this->db->prepare('SELECT * FROM scans WHERE scan_id = ?');
        $stmt->execute([$scanId]);
        $scan = $stmt->fetch();

        if (!$scan) {
            Response::notFound('Scan not found');
        }

        // Get domains
        $stmt = $this->db->prepare('SELECT domain FROM domains WHERE scan_id = ?');
        $stmt->execute([$scan['id']]);
        $scan['domains'] = $stmt->fetchAll(\PDO::FETCH_COLUMN);

        // Get findings
        $stmt = $this->db->prepare('SELECT * FROM findings WHERE scan_id = ? ORDER BY severity, created_at');
        $stmt->execute([$scan['id']]);
        $findings = $stmt->fetchAll();

        foreach ($findings as &$finding) {
            if ($finding['evidence']) {
                $finding['evidence'] = json_decode($finding['evidence'], true);
            }
        }
        $scan['findings'] = $findings;

        return $scan;
    }
}
