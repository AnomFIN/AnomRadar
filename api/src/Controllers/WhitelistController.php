<?php

declare(strict_types=1);

namespace AnomRadar\Api\Controllers;

use AnomRadar\Api\Database\Database;
use AnomRadar\Api\Utils\Response;

/**
 * Whitelist Controller - Manages whitelist for notifications
 */
class WhitelistController
{
    private Database $db;

    public function __construct(Database $db)
    {
        $this->db = $db;
    }

    public function list(): void
    {
        $type = $_GET['type'] ?? null;

        $sql = 'SELECT * FROM whitelist';
        $params = [];

        if ($type) {
            $sql .= ' WHERE entity_type = ?';
            $params[] = $type;
        }

        $sql .= ' ORDER BY entity_type, entity_value';

        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        $items = $stmt->fetchAll();

        Response::success(['whitelist' => $items]);
    }

    public function add(): void
    {
        $input = json_decode(file_get_contents('php://input'), true);
        
        if (!isset($input['entity_type']) || !isset($input['entity_value'])) {
            Response::error('entity_type and entity_value are required', 400);
        }

        $validTypes = ['domain', 'email', 'phone', 'telegram_chat', 'whatsapp_number'];
        if (!in_array($input['entity_type'], $validTypes)) {
            Response::error('Invalid entity_type', 400);
        }

        try {
            $stmt = $this->db->prepare(
                'INSERT INTO whitelist (entity_type, entity_value, description) VALUES (?, ?, ?)'
            );
            $stmt->execute([
                $input['entity_type'],
                $input['entity_value'],
                $input['description'] ?? null,
            ]);

            Response::success([
                'id' => $this->db->lastInsertId(),
                'message' => 'Added to whitelist',
            ], 201);
        } catch (\PDOException $e) {
            if ($e->getCode() === '23000') { // Duplicate entry
                Response::error('Entry already exists in whitelist', 409);
            }
            throw $e;
        }
    }

    public function remove(string $id): void
    {
        $stmt = $this->db->prepare('DELETE FROM whitelist WHERE id = ?');
        $stmt->execute([$id]);

        if ($stmt->rowCount() === 0) {
            Response::notFound('Whitelist entry not found');
        }

        Response::success(['message' => 'Removed from whitelist']);
    }
}
