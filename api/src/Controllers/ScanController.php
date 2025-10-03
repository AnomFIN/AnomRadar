<?php

declare(strict_types=1);

namespace AnomRadar\Api\Controllers;

use AnomRadar\Api\Database\Database;
use AnomRadar\Api\Utils\Response;

/**
 * Scan Controller - Manages security scans
 */
class ScanController
{
    private Database $db;

    public function __construct(Database $db)
    {
        $this->db = $db;
    }

    public function list(): void
    {
        $limit = (int)($_GET['limit'] ?? 50);
        $offset = (int)($_GET['offset'] ?? 0);
        $status = $_GET['status'] ?? null;

        $sql = 'SELECT id, scan_id, company_name, business_id, risk_score, risk_level, status, created_at, completed_at 
                FROM scans';
        
        $params = [];
        if ($status) {
            $sql .= ' WHERE status = ?';
            $params[] = $status;
        }

        $sql .= ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
        $params[] = $limit;
        $params[] = $offset;

        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        $scans = $stmt->fetchAll();

        Response::success(['scans' => $scans, 'limit' => $limit, 'offset' => $offset]);
    }

    public function get(string $id): void
    {
        $stmt = $this->db->prepare('SELECT * FROM scans WHERE scan_id = ?');
        $stmt->execute([$id]);
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

        // Decode JSON evidence
        foreach ($findings as &$finding) {
            if ($finding['evidence']) {
                $finding['evidence'] = json_decode($finding['evidence'], true);
            }
        }
        $scan['findings'] = $findings;

        Response::success($scan);
    }

    public function create(): void
    {
        $input = json_decode(file_get_contents('php://input'), true);
        
        if (!isset($input['company_name'])) {
            Response::error('company_name is required', 400);
        }

        // This would typically trigger the backend scanner
        // For now, just create a pending scan record
        $scanId = 'scan_' . time() . '_' . bin2hex(random_bytes(4));

        $stmt = $this->db->prepare(
            'INSERT INTO scans (scan_id, company_name, business_id, risk_score, risk_level, status) 
             VALUES (?, ?, ?, ?, ?, ?)'
        );
        $stmt->execute([
            $scanId,
            $input['company_name'],
            $input['business_id'] ?? null,
            0,
            'info',
            'pending',
        ]);

        Response::success(['scan_id' => $scanId, 'message' => 'Scan created'], 201);
    }

    public function delete(string $id): void
    {
        $stmt = $this->db->prepare('DELETE FROM scans WHERE scan_id = ?');
        $stmt->execute([$id]);

        if ($stmt->rowCount() === 0) {
            Response::notFound('Scan not found');
        }

        Response::success(['message' => 'Scan deleted']);
    }
}
