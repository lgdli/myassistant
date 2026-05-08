## ADDED Requirements

### Requirement: Research project links to myassistant project
The research_projects table SHALL store a `myassistant_project_id` field that uniquely references the corresponding myassistant project.

#### Scenario: Creating project with myassistant_project_id
- **WHEN** a user creates a research project with a `myassistant_project_id`
- **THEN** the project record includes the `myassistant_project_id` value
- **AND** no other project can share the same `myassistant_project_id`

#### Scenario: Creating project without myassistant_project_id
- **WHEN** a user creates a research project without providing `myassistant_project_id`
- **THEN** the `myassistant_project_id` field is NULL
- **AND** the project is created successfully

### Requirement: Sessions link to research projects explicitly
The system SHALL provide a `research_sessions` table that maps myassistant session IDs to research project IDs.

#### Scenario: Linking a session to a project
- **WHEN** a user calls `link_session` with a valid `project_id` and `session_id`
- **THEN** a new record is created in `research_sessions`
- **AND** the record includes the optional `phase` and `notes` fields if provided

#### Scenario: Linking the same session twice
- **WHEN** a user calls `link_session` with a `session_id` already linked to the same `project_id`
- **THEN** the operation returns an error indicating the session is already linked

#### Scenario: Linking a session to multiple projects
- **WHEN** a user calls `link_session` to associate the same `session_id` with different `project_id` values
- **THEN** separate records are created for each project-session pair

### Requirement: Sessions can be unlinked from research projects
The system SHALL allow removing a session association without deleting the session or project.

#### Scenario: Unlinking an existing session
- **WHEN** a user calls `unlink_session` with a valid `project_id` and `session_id`
- **THEN** the corresponding record is removed from `research_sessions`
- **AND** the myassistant session remains unaffected

#### Scenario: Unlinking a non-existent association
- **WHEN** a user calls `unlink_session` for a `project_id`/`session_id` pair that doesn't exist
- **THEN** the operation returns an error indicating no association was found

### Requirement: List all sessions for a research project
The system SHALL return all linked sessions for a given research project.

#### Scenario: Listing sessions for a project with associations
- **WHEN** a user calls `list_project_sessions` for a project with linked sessions
- **THEN** the response returns an array of objects containing `session_id`, `phase`, `notes`, and `linked_at`

#### Scenario: Listing sessions for a project with no associations
- **WHEN** a user calls `list_project_sessions` for a project with no linked sessions
- **THEN** the response returns an empty array

### Requirement: Existing MCP tools remain functional
Adding new schema changes SHALL NOT break existing tools.

#### Scenario: Creating project with old parameters
- **WHEN** a user calls `create_project` with only the original parameters (name, description, keywords, data_dir)
- **THEN** the project is created successfully with `myassistant_project_id` set to NULL

#### Scenario: Listing projects shows new field
- **WHEN** a user calls `list_projects`
- **THEN** each project record includes the `myassistant_project_id` field (NULL if not set)
