# Flow Board API Documentation

## Overview

The Flow Board API provides structured data for visualizing workflows as flow boards, similar to Kanban boards but with flow-based progression. This API endpoint returns work items organized by status columns, along with their relationships, making it compatible with frontend visualization libraries.

## Endpoint

```
GET /api/flowboard
```

## Authentication

Requires user authentication via the auth middleware.

## Query Parameters

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| `project_id` | UUID | Filter by specific project | No | null |
| `assignee_id` | UUID | Filter by assignee | No | null |
| `type` | string | Filter by work item type (task, bug, feature, epic, story, issue, pr, commit, test, deployment) | No | null |
| `priority` | string | Filter by priority (low, medium, high, critical) | No | null |
| `tags` | array[string] | Filter by tags | No | null |
| `date_from` | date | Filter items created from this date (YYYY-MM-DD) | No | null |
| `date_to` | date | Filter items created until this date (YYYY-MM-DD) | No | null |
| `limit` | integer | Maximum number of items to return | No | 1000 |

## Response Format

### FlowBoardResponse

```json
{
  "columns": [
    {
      "id": "string",
      "title": "string",
      "status": "string",
      "color": "string",
      "order": "integer",
      "item_count": "integer",
      "items": [
        {
          "id": "uuid",
          "title": "string",
          "description": "string|null",
          "type": "string",
          "status": "string",
          "priority": "string",
          "assignee_id": "uuid|null",
          "assignee_name": "string|null",
          "reporter_id": "uuid",
          "reporter_name": "string",
          "project_id": "uuid",
          "project_name": "string",
          "parent_id": "uuid|null",
          "estimated_hours": "float|null",
          "actual_hours": "float|null",
          "due_date": "date|null",
          "tags": ["string"],
          "created_at": "datetime",
          "updated_at": "datetime",
          "closed_at": "datetime|null",
          "metadata": {}
        }
      ]
    }
  ],
  "relationships": [
    {
      "source_id": "uuid",
      "target_id": "uuid",
      "relationship_type": "string",
      "description": "string|null"
    }
  ],
  "total_items": "integer",
  "filters_applied": {
    "project_id": "string|null",
    "assignee_id": "string|null",
    "type": "string|null",
    "priority": "string|null",
    "tags": ["string"]|null,
    "date_from": "string|null",
    "date_to": "string|null",
    "limit": "integer"
  },
  "generated_at": "datetime"
}
```

## Default Columns

The API provides 5 default columns (stages) representing the typical workflow progression:

1. **Backlog** (status: "open", color: "#6b7280")
2. **To Do** (status: "open", color: "#3b82f6")
3. **In Progress** (status: "in_progress", color: "#f59e0b")
4. **Review** (status: "in_progress", color: "#8b5cf6")
5. **Done** (status: "closed", color: "#10b981")

## Data Structure Details

### FlowBoardItem

Represents an individual work item in the flow board:

- **id**: Unique identifier (UUID)
- **title**: Work item title
- **description**: Optional detailed description
- **type**: Work item type (task, bug, feature, etc.)
- **status**: Current status (open, in_progress, blocked, closed, cancelled)
- **priority**: Priority level (low, medium, high, critical)
- **assignee_id/assignee_name**: Assigned user information
- **reporter_id/reporter_name**: User who created the item
- **project_id/project_name**: Associated project
- **parent_id**: Parent work item for hierarchical relationships
- **estimated_hours/actual_hours**: Time tracking
- **due_date**: Deadline
- **tags**: Array of tag strings
- **created_at/updated_at/closed_at**: Timestamps
- **metadata**: Additional custom data

### FlowBoardColumn

Represents a column/stage in the flow board:

- **id**: Column identifier
- **title**: Display name
- **status**: Status filter for items in this column
- **color**: Hex color code for UI rendering
- **order**: Display order (1-based)
- **item_count**: Number of items in this column
- **items**: Array of FlowBoardItem objects

### FlowBoardRelationship

Represents relationships between work items:

- **source_id**: Source work item UUID
- **target_id**: Target work item UUID
- **relationship_type**: Type of relationship (depends_on, blocks, relates_to, duplicates, parent_of, child_of)
- **description**: Optional relationship description

## Frontend Integration

### Compatible Libraries

The API response structure is designed to work with popular frontend visualization libraries:

- **React Flow**: Use `columns` for node positioning and `relationships` for edges
- **D3.js**: Use `columns` for force-directed layouts and `relationships` for links
- **Custom Kanban**: Direct mapping to column-based layouts

### Example Usage

```javascript
// Fetch flow board data
const response = await fetch('/api/flowboard?project_id=123e4567-e89b-12d3-a456-426614174000');
const flowBoard = await response.json();

// Access columns and items
flowBoard.columns.forEach(column => {
  console.log(`${column.title}: ${column.item_count} items`);
  column.items.forEach(item => {
    console.log(`- ${item.title} (${item.status})`);
  });
});

// Access relationships
flowBoard.relationships.forEach(rel => {
  console.log(`${rel.source_id} ${rel.relationship_type} ${rel.target_id}`);
});
```

## Filtering Examples

```bash
# Get all items for a specific project
GET /api/flowboard?project_id=123e4567-e89b-12d3-a456-426614174000

# Get high priority bugs assigned to a user
GET /api/flowboard?type=bug&priority=high&assignee_id=456e7890-e89b-12d3-a456-426614174001

# Get items created in the last month
GET /api/flowboard?date_from=2024-10-01&date_to=2024-10-31

# Get items with specific tags
GET /api/flowboard?tags=urgent&tags=frontend
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

- **400 Bad Request**: Invalid query parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied to requested resources
- **500 Internal Server Error**: Server-side errors

## Performance Considerations

- Default limit of 1000 items to prevent large responses
- Efficient database queries with proper indexing
- Relationship data included only for filtered items
- Response includes metadata about applied filters and generation time

## Future Enhancements

- Custom column configurations per project
- Real-time updates via WebSocket
- Advanced filtering options (date ranges, custom fields)
- Export functionality for different formats
- Bulk operations support